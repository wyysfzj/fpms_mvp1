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

PATH = "/api/v1/documents/{document_id}/lifecycle/application-withdrawal"
ROUTER_PATH = "/documents/{document_id}/lifecycle/application-withdrawal"
CASE_ID = "case-withdrawal-api"
DOCUMENT_ID = "document-withdrawal-request"
REQUEST_ID = "evidence-withdrawal-request"
CONFIRMATION_ID = "evidence-withdrawal-confirmation"
REVIEWED_AT = datetime(2026, 7, 30, 10, 0)
EFFECTIVE_AT = datetime(2026, 7, 30, 10, 5)


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
        "evidence_version_id": REQUEST_ID,
        "confirmation_evidence_version_id": CONFIRMATION_ID,
        "effective_at": "2026-07-30T10:05:00",
        "idempotency_key": "application-withdrawal-1",
    }
    payload.update(changes)
    return payload


def _add_evidence(
    transaction: Session,
    *,
    document_id: str,
    evidence_id: str,
    hash_char: str,
) -> None:
    transaction.add(Document(id=document_id, case_id=CASE_ID, direction="IN"))
    transaction.flush()
    attachment_id = f"attachment-{hash_char}"
    content_hash = f"sha256:{hash_char * 64}"
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"{evidence_id}.pdf",
            file_path=f"/evidence/{evidence_id}.pdf",
            mime_type="application/pdf",
            content_hash=content_hash,
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
            creator_id=f"creator-{hash_char}",
            review_state="APPROVED",
            reviewer_id=f"reviewer-{hash_char}",
            reviewed_at=REVIEWED_AT,
            content_hash=content_hash,
            current_identity_key=f"{CASE_ID}|{evidence_id}",
        )
    )


def _seed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(
            Case(
                id=CASE_ID,
                case_no="V8-WITHDRAWAL-API",
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                title_cn="撤回证据 API 测试案件",
                status="SUBSTANTIVE_EXAM",
                business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
                official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
                legal_status=LegalStatus.APPLICATION_PENDING.value,
                lifecycle_revision=0,
                lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
            )
        )
        transaction.flush()
        _add_evidence(
            transaction,
            document_id=DOCUMENT_ID,
            evidence_id=REQUEST_ID,
            hash_char="a",
        )
        _add_evidence(
            transaction,
            document_id="document-withdrawal-confirmation",
            evidence_id=CONFIRMATION_ID,
            hash_char="b",
        )
        transaction.commit()


def test_route_shape_permission_and_strict_request_are_exact() -> None:
    route = _route()
    dependency = next(item for item in route.dependant.dependencies if item.name == "_perm")
    assert route.status_code == 200
    assert inspect.getclosurevars(dependency.call).nonlocals["code"] == "Doc.Edit"
    assert tuple(_payload_type().model_fields) == (
        "evidence_version_id",
        "effective_at",
        "occurred_at",
        "idempotency_key",
        "confirmation_evidence_version_id",
    )
    assert _payload_type().model_config["extra"] == "forbid"
    with pytest.raises(ValidationError):
        _payload_type().model_validate({**_request(), "event_type": "client-owned"})


def test_two_reviewed_current_evidence_versions_map_in_fixed_order(
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
            business_stage=BusinessStage.CLOSED,
            official_procedure_stage=OfficialProcedureStage.PROCEDURE_CLOSED,
            legal_status=LegalStatus.APPLICATION_WITHDRAWN,
            lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
        )
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-withdrawal-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="APPLICATION_WITHDRAWAL_CONFIRMED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=projection,
            current_projection=projection,
            legacy_case_status="WITHDRAWN",
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
    assert response.json()["evidence_version_id"] == REQUEST_ID
    assert response.json()["confirmation_evidence_version_id"] == CONFIRMATION_ID
    assert captured[0].event_type == "APPLICATION_WITHDRAWAL_CONFIRMED"
    assert captured[0].payload == {}
    assert [
        (item.evidence_kind, item.object_id)
        for item in captured[0].evidence_refs
    ] == [
        ("APPLICATION_WITHDRAWAL_REQUEST", REQUEST_ID),
        ("APPLICATION_WITHDRAWAL_OFFICIAL_CONFIRMATION", CONFIRMATION_ID),
    ]
    assert captured[0].effective_at == EFFECTIVE_AT


def test_missing_relation_conflict_auth_and_validation_statuses(
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
    same = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(confirmation_evidence_version_id=REQUEST_ID),
    )
    assert (same.status_code, same.json()["error"]["code"]) == (
        400,
        "APPLICATION_WITHDRAWAL_EVIDENCE_RELATION_MISMATCH",
    )
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, CONFIRMATION_ID)
        assert version is not None
        version.current_identity_key = None
        transaction.commit()
    conflict = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request(),
    )
    assert (conflict.status_code, conflict.json()["error"]["code"]) == (
        409,
        "APPLICATION_WITHDRAWAL_EVIDENCE_CONFLICT",
    )
