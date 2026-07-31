from __future__ import annotations

import inspect
from datetime import datetime
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session, sessionmaker

from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case
from app.modules.documents import api as documents_api
from app.modules.documents import lifecycle_evidence_adapters as adapters
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion

PATH = "/api/v1/documents/{document_id}/lifecycle/application-rejection"
ROUTER_PATH = "/documents/{document_id}/lifecycle/application-rejection"
CASE_ID = "case-rejection-api"
DOCUMENT_ID = "document-rejection-api"
EVIDENCE_ID = "evidence-rejection-api"
CONTENT_HASH = f"sha256:{'a' * 64}"
REVIEWED_AT = datetime(2026, 7, 30, 9, 0)
EFFECTIVE_AT = datetime(2026, 7, 30, 9, 5)


def _route() -> APIRoute:
    routes = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == ROUTER_PATH
        and route.methods == {"POST"}
    ]
    assert len(routes) == 1
    return routes[0]


def _payload_type() -> type[BaseModel]:
    payload_type = get_type_hints(_route().endpoint)["payload"]
    assert isinstance(payload_type, type) and issubclass(payload_type, BaseModel)
    return payload_type


def _request(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_version_id": EVIDENCE_ID,
        "effective_at": "2026-07-30T09:05:00",
        "idempotency_key": "application-rejection-1",
        "evidence_kind": "REJECTION_DECISION",
    }
    payload.update(changes)
    return payload


def _seed(
    session_factory: sessionmaker,
    *,
    document_id: str = DOCUMENT_ID,
    evidence_id: str = EVIDENCE_ID,
) -> None:
    with session_factory() as transaction:
        if transaction.get(Case, CASE_ID) is None:
            transaction.add(
                Case(
                    id=CASE_ID,
                    case_no="V8-REJECTION-API",
                    case_type="NORMAL",
                    patent_category="INV",
                    flow_dir="CN_DOMESTIC",
                    title_cn="驳回决定证据 API 测试案件",
                    status="SUBSTANTIVE_EXAM",
                    business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
                    legal_status=LegalStatus.APPLICATION_PENDING.value,
                    lifecycle_revision=0,
                    lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
                )
            )
            transaction.flush()
        transaction.add(Document(id=document_id, case_id=CASE_ID, direction="IN"))
        transaction.flush()
        attachment_id = f"attachment-{evidence_id}"
        transaction.add(
            DocAttachment(
                id=attachment_id,
                document_id=document_id,
                file_name=f"{evidence_id}.pdf",
                file_path=f"/evidence/{evidence_id}.pdf",
                mime_type="application/pdf",
                content_hash=CONTENT_HASH,
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=evidence_id,
                case_id=CASE_ID,
                document_id=document_id,
                attachment_id=attachment_id,
                lineage_key=evidence_id,
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id="creator-rejection",
                review_state="APPROVED",
                reviewer_id="reviewer-rejection",
                reviewed_at=REVIEWED_AT,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|{evidence_id}",
            )
        )
        transaction.commit()


def test_route_request_permission_and_validation_are_exact() -> None:
    route = _route()
    dependency = next(item for item in route.dependant.dependencies if item.name == "_perm")

    assert route.status_code == 200
    assert inspect.getclosurevars(dependency.call).nonlocals["code"] == "Doc.Edit"
    assert tuple(_payload_type().model_fields) == (
        "evidence_version_id",
        "effective_at",
        "occurred_at",
        "idempotency_key",
        "evidence_kind",
    )
    assert _payload_type().model_config["extra"] == "forbid"
    with pytest.raises(ValidationError):
        _payload_type().model_validate({**_request(), "unexpected": True})
    with pytest.raises(ValidationError):
        _payload_type().model_validate(_request(effective_at="2026-07-30T09:05:00+08:00"))


@pytest.mark.parametrize(
    "evidence_kind",
    ("REJECTION_DECISION", "REEXAMINATION_FINAL_REJECTION_DECISION"),
)
def test_reviewed_current_evidence_maps_only_exact_rejection_command(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    evidence_kind: str,
) -> None:
    _seed(session_factory)
    captured: list[LifecycleEventCommand] = []

    def apply(command: LifecycleEventCommand, _transaction: Session) -> LifecycleTransitionResult:
        captured.append(command)
        projection = LifecycleProjection(
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_REJECTED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-rejection-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="APPLICATION_REJECTION_CONFIRMED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status="REJECTED",
            idempotency_key=command.idempotency_key,
            reused=False,
        )

    monkeypatch.setattr(adapters, "apply_lifecycle_event", apply)
    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(evidence_kind=evidence_kind),
    )

    assert response.status_code == 200
    assert response.json()["evidence_version_id"] == EVIDENCE_ID
    assert captured == [
        LifecycleEventCommand(
            case_id=CASE_ID,
            event_type="APPLICATION_REJECTION_CONFIRMED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=EFFECTIVE_AT,
            occurred_at=None,
            evidence_refs=(
                EvidenceReference(
                    case_id=CASE_ID,
                    evidence_kind=evidence_kind,
                    object_type="DocumentEvidenceVersion",
                    object_id=EVIDENCE_ID,
                    content_hash=CONTENT_HASH,
                    captured_at=REVIEWED_AT,
                ),
            ),
            actor_id=captured[0].actor_id,
            reviewer_id=None,
            idempotency_key="application-rejection-1",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        )
    ]


def test_relation_missing_and_conflict_statuses_are_preserved(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    missing_document = client.post(
        PATH.format(document_id="missing-document"),
        headers=auth_headers,
        json=_request(),
    )
    assert (missing_document.status_code, missing_document.json()["error"]["code"]) == (
        404,
        "DOCUMENT_NOT_FOUND",
    )

    _seed(session_factory)
    missing_evidence = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(evidence_version_id="missing-evidence"),
    )
    assert (missing_evidence.status_code, missing_evidence.json()["error"]["code"]) == (
        404,
        "EVIDENCE_VERSION_NOT_FOUND",
    )

    _seed(session_factory, document_id="other-document", evidence_id="other-evidence")
    mismatch = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(evidence_version_id="other-evidence"),
    )
    assert (mismatch.status_code, mismatch.json()["error"]["code"]) == (
        400,
        "APPLICATION_REJECTION_EVIDENCE_RELATION_MISMATCH",
    )

    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
        assert version is not None
        version.review_state = "PENDING"
        transaction.commit()
    conflict = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(),
    )
    assert (conflict.status_code, conflict.json()["error"]["code"]) == (
        409,
        "APPLICATION_REJECTION_EVIDENCE_CONFLICT",
    )


def test_endpoint_requires_authentication(client: TestClient) -> None:
    response = client.post(PATH.format(document_id=DOCUMENT_ID), json=_request())
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
