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

PATH = "/api/v1/documents/{document_id}/lifecycle/application-restoration"
ROUTER_PATH = "/documents/{document_id}/lifecycle/application-restoration"
CASE_ID = "case-restoration-api"
DOCUMENT_ID = "document-restoration-api"
EVIDENCE_ID = "evidence-restoration-api"
REVIEWED_AT = datetime(2026, 7, 30, 13, 55)
CONTENT_HASH = f"sha256:{'d' * 64}"


def _route() -> APIRoute:
    matches = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == ROUTER_PATH
        and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _payload_type() -> type[BaseModel]:
    result = get_type_hints(_route().endpoint)["payload"]
    assert isinstance(result, type) and issubclass(result, BaseModel)
    return result


def _request(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_version_id": EVIDENCE_ID,
        "effective_at": "2026-07-30T14:00:00",
        "idempotency_key": "application-restoration-1",
        "restored_official_procedure_stage": "SUBSTANTIVE_EXAMINATION",
    }
    payload.update(changes)
    return payload


def _seed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="V8-RESTORATION-API",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="申请权利恢复证据 API 测试案件",
                status="ABANDONED",
                business_stage=BusinessStage.CLOSED.value,
                official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED.value,
                legal_status=LegalStatus.APPLICATION_ABANDONED.value,
                lifecycle_revision=0,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            )
        )
        transaction.flush()
        transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"))
        transaction.flush()
        transaction.add(
            DocAttachment(
                id="attachment-restoration-api",
                document_id=DOCUMENT_ID,
                file_name="restoration.pdf",
                file_path="/evidence/restoration.pdf",
                mime_type="application/pdf",
                content_hash=CONTENT_HASH,
            )
        )
        transaction.flush()
        transaction.add(
            DocumentEvidenceVersion(
                id=EVIDENCE_ID,
                case_id=CASE_ID,
                document_id=DOCUMENT_ID,
                attachment_id="attachment-restoration-api",
                lineage_key="restoration",
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id="creator-restoration",
                review_state="APPROVED",
                reviewer_id="reviewer-restoration",
                reviewed_at=REVIEWED_AT,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|restoration",
            )
        )
        transaction.commit()


def test_route_shape_permission_and_restored_stage_boundary_are_exact() -> None:
    route = _route()
    dependency = next(item for item in route.dependant.dependencies if item.name == "_perm")
    assert route.status_code == 200
    assert inspect.getclosurevars(dependency.call).nonlocals["code"] == "Doc.Edit"
    assert tuple(_payload_type().model_fields) == (
        "evidence_version_id",
        "effective_at",
        "occurred_at",
        "idempotency_key",
        "restored_official_procedure_stage",
    )
    with pytest.raises(ValidationError):
        _payload_type().model_validate(
            _request(restored_official_procedure_stage="PROCEDURE_CLOSED")
        )


def test_reviewed_decision_maps_only_restoration_with_explicit_stage(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed(session_factory)
    captured: list[LifecycleEventCommand] = []

    def apply(command: LifecycleEventCommand, _transaction: Session) -> LifecycleTransitionResult:
        captured.append(command)
        projection = LifecycleProjection(
            business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
            official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
            legal_status=LegalStatus.APPLICATION_PENDING,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-restoration-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="APPLICATION_RIGHT_RESTORATION_CONFIRMED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status="SUBSTANTIVE_EXAM",
            idempotency_key=command.idempotency_key,
            reused=False,
        )

    monkeypatch.setattr(adapters, "apply_lifecycle_event", apply)
    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(),
    )
    assert response.status_code == 200
    assert captured[0].event_type == "APPLICATION_RIGHT_RESTORATION_CONFIRMED"
    assert captured[0].evidence_refs[0].evidence_kind == (
        "APPLICATION_RIGHT_RESTORATION_DECISION"
    )
    assert captured[0].payload == {
        "restored_official_procedure_stage": "SUBSTANTIVE_EXAMINATION"
    }


def test_auth_validation_missing_and_conflict_statuses(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    assert client.post(PATH.format(document_id=DOCUMENT_ID), json=_request()).status_code == 401
    invalid = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json={**_request(), "unexpected": True},
    )
    assert invalid.status_code == 422
    missing = client.post(
        PATH.format(document_id="missing-document"),
        headers=auth_headers,
        json=_request(),
    )
    assert (missing.status_code, missing.json()["error"]["code"]) == (
        404,
        "DOCUMENT_NOT_FOUND",
    )

    _seed(session_factory)
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_ID)
        assert version is not None
        version.reviewer_id = version.creator_id
        transaction.commit()
    conflict = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(),
    )
    assert (conflict.status_code, conflict.json()["error"]["code"]) == (
        409,
        "APPLICATION_RESTORATION_EVIDENCE_CONFLICT",
    )
