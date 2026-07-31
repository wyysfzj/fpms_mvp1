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

PATH = "/api/v1/documents/{document_id}/lifecycle/application-abandonment"
ROUTER_PATH = "/documents/{document_id}/lifecycle/application-abandonment"
CASE_ID = "case-abandonment-api"
DOCUMENT_ID = "document-abandonment-api"
EVIDENCE_ID = "evidence-abandonment-api"
REVIEWED_AT = datetime(2026, 7, 30, 11, 0)
CONTENT_HASH = f"sha256:{'c' * 64}"


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
        "evidence_kind": "DEEMED_ABANDONMENT_NOTICE",
        "effective_at": "2026-07-30T11:05:00",
        "idempotency_key": "application-abandonment-1",
    }
    payload.update(changes)
    return payload


def _seed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="V8-ABANDONMENT-API",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="视为放弃证据 API 测试案件",
                status="SUBSTANTIVE_EXAM",
                business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
                legal_status=LegalStatus.APPLICATION_PENDING.value,
                lifecycle_revision=0,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            )
        )
        transaction.flush()
        transaction.add(Document(id=DOCUMENT_ID, case_id=CASE_ID, direction="IN"))
        transaction.flush()
        transaction.add(
            DocAttachment(
                id="attachment-abandonment-api",
                document_id=DOCUMENT_ID,
                file_name="abandonment.pdf",
                file_path="/evidence/abandonment.pdf",
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
                attachment_id="attachment-abandonment-api",
                lineage_key="abandonment",
                role="OFFICIAL_FINAL_PDF",
                version_number=1,
                state="FINAL",
                creator_id="creator-abandonment",
                review_state="APPROVED",
                reviewer_id="reviewer-abandonment",
                reviewed_at=REVIEWED_AT,
                content_hash=CONTENT_HASH,
                current_identity_key=f"{CASE_ID}|abandonment",
            )
        )
        transaction.commit()


def test_route_shape_permission_and_request_boundary_are_exact() -> None:
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
    with pytest.raises(ValidationError):
        _payload_type().model_validate(_request(evidence_kind="ARBITRARY"))


@pytest.mark.parametrize(
    "evidence_kind",
    ("DEEMED_ABANDONMENT_NOTICE", "RIGHT_ABANDONMENT_CONFIRMATION"),
)
def test_allowed_evidence_maps_only_application_abandonment(
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
            legal_status=LegalStatus.APPLICATION_ABANDONED,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-abandonment-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="APPLICATION_ABANDONMENT_CONFIRMED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status="ABANDONED",
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
    assert captured[0].event_type == "APPLICATION_ABANDONMENT_CONFIRMED"
    assert captured[0].evidence_refs[0].evidence_kind == evidence_kind
    assert captured[0].evidence_refs[0].object_id == EVIDENCE_ID
    assert captured[0].payload == {}


def test_auth_validation_missing_relation_and_conflict_statuses(
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
        version.review_state = "PENDING"
        transaction.commit()
    conflict = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(),
    )
    assert (conflict.status_code, conflict.json()["error"]["code"]) == (
        409,
        "APPLICATION_ABANDONMENT_EVIDENCE_CONFLICT",
    )
