from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass
from datetime import datetime
from importlib import import_module
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.errors import BusinessError
from app.core.security import create_access_token
from app.db.session import get_db
from app.main import create_app
from app.modules.auth.models import T_User
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
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents import api as documents_api
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion

PATH = "/api/v1/documents/{document_id}/lifecycle/preliminary-start"
ROUTER_PATH = "/documents/{document_id}/lifecycle/preliminary-start"
CASE_ID = "case-preliminary-api"
DOCUMENT_ID = "document-preliminary-api"
ATTACHMENT_ID = "attachment-preliminary-api"
EVIDENCE_VERSION_ID = "evidence-preliminary-api"
OTHER_CASE_ID = "case-preliminary-other"
OTHER_DOCUMENT_ID = "document-preliminary-other"
OTHER_ATTACHMENT_ID = "attachment-preliminary-other"
OTHER_EVIDENCE_VERSION_ID = "evidence-preliminary-other"
ALT_ATTACHMENT_ID = "attachment-preliminary-alt"
ALT_EVIDENCE_VERSION_ID = "evidence-preliminary-alt"
ACTOR_USERNAME = "admin"
CREATOR_ID = "evidence-creator"
REVIEWER_ID = "evidence-reviewer"
EFFECTIVE_AT = datetime(2026, 7, 20, 10, 30)
OCCURRED_AT = datetime(2026, 7, 20, 10, 15)
REVIEWED_AT = datetime(2026, 7, 20, 9, 45)
CONTENT_HASH = f"sha256:{'a' * 64}"
ADAPTER_MODULE = "app.modules.documents.lifecycle_evidence_adapters"

ACCEPTED_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.ACCEPTED,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
PRELIMINARY_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)

REQUEST_FIELDS = (
    "evidence_version_id",
    "effective_at",
    "occurred_at",
    "idempotency_key",
)
RESPONSE_FIELDS = (
    "case_id",
    "document_id",
    "evidence_version_id",
    "activity_id",
    "activity_sequence",
    "lifecycle_revision",
    "effective_at",
    "occurred_at",
    "idempotency_key",
    "reused",
)


class RecordingSession:
    def __init__(self, transaction: Session) -> None:
        self.transaction = transaction
        self.commit_calls = 0
        self.rollback_calls = 0

    def __getattr__(self, name: str) -> object:
        return getattr(self.transaction, name)

    def commit(self) -> None:
        self.commit_calls += 1
        self.transaction.commit()

    def rollback(self) -> None:
        self.rollback_calls += 1
        self.transaction.rollback()


def _request_data(
    *,
    evidence_version_id: str = EVIDENCE_VERSION_ID,
    effective_at: str = "2026-07-20T10:30:00",
    occurred_at: str | None = None,
    idempotency_key: str = "preliminary-start-1",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_version_id": evidence_version_id,
        "effective_at": effective_at,
        "idempotency_key": idempotency_key,
    }
    if occurred_at is not None:
        payload["occurred_at"] = occurred_at
    return payload


def _route() -> APIRoute:
    matching = [
        route
        for route in documents_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"POST"}
    ]
    assert len(matching) == 1
    return matching[0]


def _payload_type() -> type[BaseModel]:
    payload_type = get_type_hints(_route().endpoint)["payload"]
    assert isinstance(payload_type, type)
    assert issubclass(payload_type, BaseModel)
    return payload_type


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _response_field_names(response_model: object) -> tuple[str, ...]:
    if isinstance(response_model, type) and issubclass(response_model, BaseModel):
        return tuple(response_model.model_fields)
    assert isinstance(response_model, type)
    assert is_dataclass(response_model)
    return tuple(field.name for field in fields(response_model))


def _case(
    *,
    case_id: str = CASE_ID,
    case_no: str = "V8-PRELIMINARY-API",
) -> Case:
    return Case(
        id=case_id,
        case_no=case_no,
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="初步审查开始证据 API 测试案件",
        status="ACCEPTED",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.ACCEPTED.value,
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_revision=0,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
    )


def _add_document_evidence(
    transaction: Session,
    *,
    case_id: str,
    document_id: str,
    attachment_id: str,
    evidence_version_id: str,
    lineage_key: str,
) -> DocumentEvidenceVersion:
    transaction.add(Document(id=document_id, case_id=case_id, direction="IN"))
    transaction.flush()
    transaction.add(
        DocAttachment(
            id=attachment_id,
            document_id=document_id,
            file_name=f"{evidence_version_id}.pdf",
            file_path=f"/evidence/{evidence_version_id}.pdf",
            mime_type="application/pdf",
            content_hash=CONTENT_HASH,
        )
    )
    transaction.flush()
    version = DocumentEvidenceVersion(
        id=evidence_version_id,
        case_id=case_id,
        document_id=document_id,
        attachment_id=attachment_id,
        lineage_key=lineage_key,
        role="OFFICIAL_FINAL_PDF",
        version_number=1,
        state="FINAL",
        creator_id=CREATOR_ID,
        review_state="APPROVED",
        reviewer_id=REVIEWER_ID,
        reviewed_at=REVIEWED_AT,
        content_hash=CONTENT_HASH,
        current_identity_key=f"{case_id}|{lineage_key}",
    )
    transaction.add(version)
    return version


def _seed_valid_evidence(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.flush()
        _add_document_evidence(
            transaction,
            case_id=CASE_ID,
            document_id=DOCUMENT_ID,
            attachment_id=ATTACHMENT_ID,
            evidence_version_id=EVIDENCE_VERSION_ID,
            lineage_key="preliminary-source",
        )
        transaction.commit()


def _add_alternate_evidence(
    session_factory: sessionmaker,
    *,
    relationship: str = "same_document",
) -> None:
    with session_factory() as transaction:
        if relationship == "same_document":
            transaction.add(
                DocAttachment(
                    id=ALT_ATTACHMENT_ID,
                    document_id=DOCUMENT_ID,
                    file_name="preliminary-alt.pdf",
                    file_path="/evidence/preliminary-alt.pdf",
                    mime_type="application/pdf",
                    content_hash=CONTENT_HASH,
                )
            )
            transaction.flush()
            transaction.add(
                DocumentEvidenceVersion(
                    id=ALT_EVIDENCE_VERSION_ID,
                    case_id=CASE_ID,
                    document_id=DOCUMENT_ID,
                    attachment_id=ALT_ATTACHMENT_ID,
                    lineage_key="preliminary-source-alt",
                    role="OFFICIAL_FINAL_PDF",
                    version_number=1,
                    state="FINAL",
                    creator_id=CREATOR_ID,
                    review_state="APPROVED",
                    reviewer_id=REVIEWER_ID,
                    reviewed_at=REVIEWED_AT,
                    content_hash=CONTENT_HASH,
                    current_identity_key=f"{CASE_ID}|preliminary-source-alt",
                )
            )
        elif relationship == "other_document":
            _add_document_evidence(
                transaction,
                case_id=CASE_ID,
                document_id=OTHER_DOCUMENT_ID,
                attachment_id=OTHER_ATTACHMENT_ID,
                evidence_version_id=OTHER_EVIDENCE_VERSION_ID,
                lineage_key="preliminary-source-other-document",
            )
        elif relationship == "other_case":
            transaction.add(
                _case(
                    case_id=OTHER_CASE_ID,
                    case_no="V8-PRELIMINARY-API-OTHER",
                )
            )
            transaction.flush()
            _add_document_evidence(
                transaction,
                case_id=OTHER_CASE_ID,
                document_id=OTHER_DOCUMENT_ID,
                attachment_id=OTHER_ATTACHMENT_ID,
                evidence_version_id=OTHER_EVIDENCE_VERSION_ID,
                lineage_key="preliminary-source-other-case",
            )
        else:
            raise AssertionError(f"unknown relationship fixture: {relationship}")
        transaction.commit()


def _adapter_module():
    return import_module(ADAPTER_MODULE)


def _assert_case_unchanged(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
            case.lifecycle_verification_status,
        ) == (
            "ACCEPTED",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.ACCEPTED.value,
            LegalStatus.APPLICATION_PENDING.value,
            0,
            ConfirmationStatus.CONFIRMED.value,
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == CASE_ID)
            )
            == 0
        )


def _authenticated_actor_id(session_factory: sessionmaker) -> str:
    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == ACTOR_USERNAME))
    assert actor_id is not None
    return actor_id


def _client_for_transaction(transaction: object) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    return TestClient(app)


def test_route_is_the_only_post_with_doc_edit_and_server_owned_context() -> None:
    route = _route()

    assert route.status_code == 200
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    assert next(item.call for item in route.dependant.dependencies if item.name == "db") is get_db
    assert list(inspect.signature(route.endpoint).parameters) == [
        "document_id",
        "payload",
        "_perm",
        "current_user",
        "db",
    ]
    assert _response_field_names(route.response_model) == RESPONSE_FIELDS


def test_strict_request_has_only_delta8_fields_and_preserves_absent_occurred_at() -> None:
    payload_type = _payload_type()

    assert tuple(payload_type.model_fields) == REQUEST_FIELDS
    assert get_type_hints(payload_type) == {
        "evidence_version_id": str,
        "effective_at": datetime,
        "occurred_at": datetime | None,
        "idempotency_key": str,
    }
    assert payload_type.model_config["extra"] == "forbid"
    assert payload_type.model_fields["evidence_version_id"].is_required()
    assert payload_type.model_fields["effective_at"].is_required()
    assert not payload_type.model_fields["occurred_at"].is_required()
    assert payload_type.model_fields["occurred_at"].default is None
    assert payload_type.model_fields["idempotency_key"].is_required()
    assert payload_type.model_validate(_request_data()).model_dump() == {
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "effective_at": EFFECTIVE_AT,
        "occurred_at": None,
        "idempotency_key": "preliminary-start-1",
    }
    assert (
        payload_type.model_validate(_request_data(occurred_at="2026-07-20T10:15:00")).occurred_at
        == OCCURRED_AT
    )


@pytest.mark.parametrize(
    "invalid",
    (
        {key: value for key, value in _request_data().items() if key != "evidence_version_id"},
        {key: value for key, value in _request_data().items() if key != "effective_at"},
        {key: value for key, value in _request_data().items() if key != "idempotency_key"},
        {**_request_data(), "unexpected": True},
        {**_request_data(), "case_id": "client-case"},
        {**_request_data(), "document_id": DOCUMENT_ID},
        {**_request_data(), "event_type": "PRELIMINARY_EXAMINATION_STARTED"},
        {**_request_data(), "actor_id": "client-actor"},
        {**_request_data(), "reviewer_id": "client-reviewer"},
        {**_request_data(), "evidence_version_id": 1},
        {**_request_data(), "idempotency_key": 1},
        {**_request_data(), "effective_at": "not-a-datetime"},
        {**_request_data(), "effective_at": "2026-07-20T10:30:00+08:00"},
        {**_request_data(), "occurred_at": "2026-07-20T10:15:00+08:00"},
    ),
)
def test_missing_extra_client_owned_wrong_type_and_aware_inputs_fail_422_validation(
    invalid: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        _payload_type().model_validate(invalid)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: object()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None

    with TestClient(app) as client:
        response = client.post(PATH.format(document_id=DOCUMENT_ID), json=invalid)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_direct_response_has_exact_delta8_annotations() -> None:
    response_model = _route().response_model

    assert response_model is not None
    assert get_type_hints(response_model) == {
        "case_id": str,
        "document_id": str,
        "evidence_version_id": str,
        "activity_id": str,
        "activity_sequence": int,
        "lifecycle_revision": int,
        "effective_at": datetime,
        "occurred_at": datetime | None,
        "idempotency_key": str,
        "reused": bool,
    }


def test_valid_evidence_maps_exact_lifecycle_command_once_and_commits_once(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid_evidence(session_factory)
    actor_id = _authenticated_actor_id(session_factory)
    captured: list[LifecycleEventCommand] = []

    def apply(
        command: LifecycleEventCommand,
        _transaction: object,
    ) -> LifecycleTransitionResult:
        captured.append(command)
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-preliminary-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="PRELIMINARY_EXAMINATION_STARTED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=ACCEPTED_PROJECTION,
            current_projection=PRELIMINARY_PROJECTION,
            legacy_case_status="PRELIM_EXAM",
            idempotency_key=command.idempotency_key,
            reused=False,
        )

    monkeypatch.setattr(_adapter_module(), "apply_lifecycle_event", apply)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        with _client_for_transaction(recording) as client:
            response = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=_request_data(occurred_at="2026-07-20T10:15:00"),
            )

    assert response.status_code == 200
    assert tuple(response.json()) == RESPONSE_FIELDS
    assert response.json() == {
        "case_id": CASE_ID,
        "document_id": DOCUMENT_ID,
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "activity_id": "activity-preliminary-api",
        "activity_sequence": 1,
        "lifecycle_revision": 1,
        "effective_at": "2026-07-20T10:30:00",
        "occurred_at": "2026-07-20T10:15:00",
        "idempotency_key": "preliminary-start-1",
        "reused": False,
    }
    assert captured == [
        LifecycleEventCommand(
            case_id=CASE_ID,
            event_type="PRELIMINARY_EXAMINATION_STARTED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=EFFECTIVE_AT,
            occurred_at=OCCURRED_AT,
            evidence_refs=(
                EvidenceReference(
                    case_id=CASE_ID,
                    evidence_kind="PRELIMINARY_EXAMINATION_SOURCE",
                    object_type="DocumentEvidenceVersion",
                    object_id=EVIDENCE_VERSION_ID,
                    content_hash=CONTENT_HASH,
                    captured_at=REVIEWED_AT,
                ),
            ),
            actor_id=actor_id,
            reviewer_id=None,
            idempotency_key="preliminary-start-1",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        )
    ]
    assert recording.commit_calls == 1
    assert recording.rollback_calls == 0


@pytest.mark.parametrize("occurred_at", (None, "2026-07-20T10:15:00"))
def test_fresh_and_replay_return_direct_200_and_persist_one_exact_activity(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    occurred_at: str | None,
) -> None:
    _seed_valid_evidence(session_factory)
    payload = _request_data(occurred_at=occurred_at)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        with _client_for_transaction(recording) as client:
            fresh = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=payload,
            )
            replay = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=payload,
            )

    assert fresh.status_code == replay.status_code == 200
    assert tuple(fresh.json()) == tuple(replay.json()) == RESPONSE_FIELDS
    assert fresh.json()["reused"] is False
    assert replay.json() == {**fresh.json(), "reused": True}
    assert fresh.json()["occurred_at"] == occurred_at
    assert recording.commit_calls == 2
    assert recording.rollback_calls == 0

    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == CASE_ID)
        ).all()
        assert case is not None
        assert len(activities) == 1
        activity = activities[0]
        assert (
            activity.lane,
            activity.activity_type,
            activity.confirmation_status,
            activity.old_business_stage,
            activity.new_business_stage,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.old_legal_status,
            activity.new_legal_status,
            activity.effective_at,
            activity.occurred_at,
        ) == (
            ActivityLane.LIFECYCLE.value,
            "PRELIMINARY_EXAMINATION_STARTED",
            ConfirmationStatus.CONFIRMED.value,
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.ACCEPTED.value,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            LegalStatus.APPLICATION_PENDING.value,
            EFFECTIVE_AT,
            None if occurred_at is None else OCCURRED_AT,
        )
        evidence = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert [
            (
                item.evidence_kind,
                item.object_type,
                item.object_id,
                item.content_hash,
                item.captured_at,
            )
            for item in evidence
        ] == [
            (
                "PRELIMINARY_EXAMINATION_SOURCE",
                "DocumentEvidenceVersion",
                EVIDENCE_VERSION_ID,
                CONTENT_HASH,
                REVIEWED_AT,
            )
        ]
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
        ) == (
            "PRELIM_EXAM",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            1,
        )


@pytest.mark.parametrize("relationship", ("other_document", "other_case"))
def test_wrong_document_or_case_relationship_is_exact_400_without_partial_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    relationship: str,
) -> None:
    _seed_valid_evidence(session_factory)
    _add_alternate_evidence(session_factory, relationship=relationship)

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == ("PRELIMINARY_START_EVIDENCE_RELATION_MISMATCH")
    assert response.json()["error"]["details"] == {"field": "evidence_version_id"}
    _assert_case_unchanged(session_factory)


@pytest.mark.parametrize(
    ("missing", "code"),
    (
        ("document", "DOCUMENT_NOT_FOUND"),
        ("evidence", "EVIDENCE_VERSION_NOT_FOUND"),
    ),
)
def test_missing_document_or_evidence_preserves_exact_404(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    missing: str,
    code: str,
) -> None:
    if missing == "evidence":
        _seed_valid_evidence(session_factory)
    document_id = "missing-document" if missing == "document" else DOCUMENT_ID

    response = client.post(
        PATH.format(document_id=document_id),
        headers=auth_headers,
        json=_request_data(evidence_version_id="missing-evidence"),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == code
    if missing == "evidence":
        _assert_case_unchanged(session_factory)


def _invalidate_evidence(version: DocumentEvidenceVersion, conflict: str) -> None:
    if conflict == "non_current":
        version.current_identity_key = None
    elif conflict == "non_final":
        version.state = "DRAFT"
    elif conflict == "non_approved":
        version.review_state = "PENDING"
        version.reviewer_id = None
        version.reviewed_at = None
    elif conflict == "wrong_role":
        version.role = "OFFICIAL_NOTICE"
    elif conflict == "self_review":
        version.reviewer_id = version.creator_id
    elif conflict == "malformed_hash":
        version.content_hash = "sha256:not-canonical"
    elif conflict == "whitespace_lineage":
        version.lineage_key = f"{version.lineage_key} "
        version.current_identity_key = f"{version.case_id}|{version.lineage_key}"
    elif conflict == "whitespace_creator":
        version.creator_id = f" {version.creator_id}"
    elif conflict == "whitespace_reviewer":
        version.reviewer_id = f"{version.reviewer_id} "
    else:
        raise AssertionError(f"unknown evidence conflict fixture: {conflict}")


@pytest.mark.parametrize(
    "conflict",
    (
        "non_current",
        "non_final",
        "non_approved",
        "wrong_role",
        "self_review",
        "malformed_hash",
        "whitespace_lineage",
        "whitespace_creator",
        "whitespace_reviewer",
    ),
)
def test_stored_evidence_conflicts_are_exact_409_without_partial_status(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    conflict: str,
) -> None:
    _seed_valid_evidence(session_factory)
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert version is not None
        _invalidate_evidence(version, conflict)
        transaction.commit()

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PRELIMINARY_START_EVIDENCE_CONFLICT"
    assert response.json()["error"]["details"] == {"field": "evidence_version_id"}
    _assert_case_unchanged(session_factory)


@pytest.mark.parametrize("changed", ("effective_at", "evidence_version_id"))
def test_same_key_with_changed_command_or_evidence_is_idempotency_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    changed: str,
) -> None:
    _seed_valid_evidence(session_factory)
    _add_alternate_evidence(session_factory)
    first = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    changed_payload = (
        _request_data(effective_at="2026-07-20T10:31:00")
        if changed == "effective_at"
        else _request_data(evidence_version_id=ALT_EVIDENCE_VERSION_ID)
    )

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=changed_payload,
    )

    assert first.status_code == 200
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert case.lifecycle_revision == 1
        assert case.official_procedure_stage == (
            OfficialProcedureStage.PRELIMINARY_EXAMINATION.value
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == CASE_ID)
            )
            == 1
        )


def test_authentication_and_doc_edit_permission_preserve_401_and_403(
    client: TestClient,
    session_factory: sessionmaker,
) -> None:
    unauthenticated = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        json=_request_data(),
    )
    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    user_id = "preliminary-no-permission-user"
    with session_factory() as transaction:
        user = T_User(
            id=user_id,
            username="preliminary-no-permission",
            display_name="无权限用户",
            password_hash="unused",
            is_active=True,
        )
        transaction.add(user)
        transaction.commit()
    token = create_access_token(
        subject=user_id,
        secret=get_settings().jwt_secret,
        expires_minutes=60,
    )
    forbidden = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers={"Authorization": f"Bearer {token}"},
        json=_request_data(),
    )

    assert forbidden.status_code == 403
    assert forbidden.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Doc.Edit"},
        }
    }


@pytest.mark.parametrize(
    ("status_code", "code"),
    (
        (404, "CASE_NOT_FOUND"),
        (400, "LIFECYCLE_EVENT_INVALID"),
        (409, "LIFECYCLE_RULE_NOT_REGISTERED"),
        (409, "LIFECYCLE_RULE_RESOLUTION_FAILED"),
        (409, "LIFECYCLE_RULE_DECISION_INVALID"),
        (409, "LIFECYCLE_PROJECTION_CONFLICT"),
        (409, "LIFECYCLE_LEGACY_PROJECTION_CONFLICT"),
    ),
)
def test_deeper_lifecycle_errors_pass_through_and_roll_back_without_partial_status(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    _seed_valid_evidence(session_factory)

    def fail(command: LifecycleEventCommand, transaction: Session) -> None:
        case = transaction.get(Case, command.case_id)
        assert case is not None
        case.official_procedure_stage = OfficialProcedureStage.PRELIMINARY_EXAMINATION.value
        transaction.flush()
        raise BusinessError(
            code,
            "deeper lifecycle error",
            details={"marker": code},
            status_code=status_code,
        )

    monkeypatch.setattr(_adapter_module(), "apply_lifecycle_event", fail)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        with _client_for_transaction(recording) as client:
            response = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=_request_data(),
            )

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "deeper lifecycle error",
            "details": {"marker": code},
        }
    }
    assert recording.commit_calls == 0
    assert recording.rollback_calls == 1
    _assert_case_unchanged(session_factory)
