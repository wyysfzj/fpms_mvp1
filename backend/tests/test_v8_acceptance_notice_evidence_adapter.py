from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass, replace
from datetime import datetime, timezone
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
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.documents.semantics import resolve_document_semantics

PATH = "/api/v1/documents/{document_id}/lifecycle/acceptance-notice"
ROUTER_PATH = "/documents/{document_id}/lifecycle/acceptance-notice"
CASE_ID = "case-acceptance-api"
DOCUMENT_ID = "document-acceptance-api"
ATTACHMENT_ID = "attachment-acceptance-api"
EVIDENCE_VERSION_ID = "evidence-acceptance-api"
OTHER_DOCUMENT_ID = "document-acceptance-other"
OTHER_ATTACHMENT_ID = "attachment-acceptance-other"
OTHER_EVIDENCE_VERSION_ID = "evidence-acceptance-other"
OTHER_CASE_ID = "case-acceptance-other"
ACTOR_USERNAME = "admin"
CREATOR_ID = "acceptance-creator"
REVIEWER_ID = "acceptance-reviewer"
EFFECTIVE_AT = datetime(2026, 7, 24, 15, 0)
OCCURRED_AT = datetime(2026, 7, 24, 14, 55)
REVIEWED_AT = datetime(2026, 7, 24, 14, 30)
CONTENT_HASH = f"sha256:{'a' * 64}"
ADAPTER_MODULE = "app.modules.documents.lifecycle_evidence_adapters"

WAITING_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
ACCEPTED_PROJECTION = replace(
    WAITING_PROJECTION,
    official_procedure_stage=OfficialProcedureStage.ACCEPTED,
)
REQUEST_FIELDS = (
    "evidence_version_id",
    "effective_at",
    "occurred_at",
    "idempotency_key",
)
COMMAND_FIELDS = (
    "document_id",
    "evidence_version_id",
    "actor_id",
    "effective_at",
    "occurred_at",
    "idempotency_key",
)
RESULT_FIELDS = (
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


class StringSubclass(str):
    pass


class DatetimeSubclass(datetime):
    pass


class RecordingSession:
    def __init__(self, transaction: Session) -> None:
        self.transaction = transaction
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    def __getattr__(self, name: str) -> object:
        return getattr(self.transaction, name)

    def commit(self) -> None:
        self.commit_calls += 1
        self.transaction.commit()

    def rollback(self) -> None:
        self.rollback_calls += 1
        self.transaction.rollback()

    def close(self) -> None:
        self.close_calls += 1
        self.transaction.close()


def _adapter():
    return import_module(ADAPTER_MODULE)


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
    assert isinstance(payload_type, type) and issubclass(payload_type, BaseModel)
    return payload_type


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _request_data(
    *,
    evidence_version_id: str = EVIDENCE_VERSION_ID,
    effective_at: str = "2026-07-24T15:00:00",
    occurred_at: str | None = None,
    idempotency_key: str = "acceptance-notice-1",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_version_id": evidence_version_id,
        "effective_at": effective_at,
        "idempotency_key": idempotency_key,
    }
    if occurred_at is not None:
        payload["occurred_at"] = occurred_at
    return payload


def _case() -> Case:
    return Case(
        id=CASE_ID,
        case_no="V8-ACCEPTANCE-API",
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="受理通知证据适配测试案件",
        status="WAITING_RECEIPT",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=(
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE.value
        ),
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_revision=0,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
    )


def _template(*, template_id: str = "template-acceptance-api") -> DocTemplate:
    return DocTemplate(
        id=template_id,
        code=f"ACCEPTANCE_NOTICE_{template_id[-3:]}",
        name="受理通知书",
        direction="IN",
        enabled=True,
        status_effect="ACCEPTED",
        need_reply=False,
        input_fields=(
            '{"catalog_kind":"OFFICIAL_NOTICE",'
            '"catalog_status":"EXECUTABLE",'
            '"execution_behavior":"ACCEPTANCE_NOTICE",'
            '"canonical_template_code":"ACCEPTANCE_NOTICE"}'
        ),
    )


def _document(
    *,
    document_id: str = DOCUMENT_ID,
    template_id: str = "template-acceptance-api",
    direction: str = "IN",
) -> Document:
    return Document(
        id=document_id,
        case_id=CASE_ID,
        doc_template_id=template_id,
        direction=direction,
        title="受理通知书",
    )


def _attachment(
    *,
    attachment_id: str = ATTACHMENT_ID,
    document_id: str = DOCUMENT_ID,
) -> DocAttachment:
    return DocAttachment(
        id=attachment_id,
        document_id=document_id,
        file_name="acceptance.pdf",
        file_path=f"/evidence/{attachment_id}.pdf",
        content_hash=CONTENT_HASH,
    )


def _version(
    *,
    version_id: str = EVIDENCE_VERSION_ID,
    document_id: str = DOCUMENT_ID,
    attachment_id: str = ATTACHMENT_ID,
    lineage_key: str = "acceptance-final",
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=version_id,
        case_id=CASE_ID,
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
        current_identity_key=f"{CASE_ID}|{lineage_key}",
    )


def _seed_valid(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        transaction.add(_template())
        transaction.flush()
        transaction.add(_document())
        transaction.flush()
        transaction.add(_attachment())
        transaction.flush()
        transaction.add(_version())
        transaction.commit()


def _add_other_evidence(
    session_factory: sessionmaker,
    *,
    relationship: str = "other_document",
) -> None:
    with session_factory() as transaction:
        case_id = CASE_ID
        if relationship == "other_case":
            other_case = _case()
            other_case.id = OTHER_CASE_ID
            other_case.case_no = "V8-ACCEPTANCE-OTHER"
            transaction.add(other_case)
            case_id = OTHER_CASE_ID
        other_document = _document(document_id=OTHER_DOCUMENT_ID)
        other_document.case_id = case_id
        transaction.add(other_document)
        transaction.flush()
        transaction.add(
            _attachment(
                attachment_id=OTHER_ATTACHMENT_ID,
                document_id=OTHER_DOCUMENT_ID,
            )
        )
        transaction.flush()
        other_version = _version(
            version_id=OTHER_EVIDENCE_VERSION_ID,
            document_id=OTHER_DOCUMENT_ID,
            attachment_id=OTHER_ATTACHMENT_ID,
            lineage_key="acceptance-other",
        )
        other_version.case_id = case_id
        other_version.current_identity_key = f"{case_id}|acceptance-other"
        transaction.add(other_version)
        transaction.commit()


def _add_alternate_same_document_evidence(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        transaction.add(
            _attachment(
                attachment_id=OTHER_ATTACHMENT_ID,
                document_id=DOCUMENT_ID,
            )
        )
        transaction.flush()
        transaction.add(
            _version(
                version_id=OTHER_EVIDENCE_VERSION_ID,
                document_id=DOCUMENT_ID,
                attachment_id=OTHER_ATTACHMENT_ID,
                lineage_key="acceptance-alternate",
            )
        )
        transaction.commit()


def _actor_id(session_factory: sessionmaker) -> str:
    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == ACTOR_USERNAME))
    assert actor_id is not None
    return actor_id


def _client_for(transaction: object) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    return TestClient(app)


def _assert_no_acceptance_write(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        document = transaction.get(Document, DOCUMENT_ID)
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert case is not None and document is not None and version is not None
        assert (
            case.status,
            case.business_stage,
            case.official_procedure_stage,
            case.legal_status,
            case.lifecycle_revision,
        ) == (
            "WAITING_RECEIPT",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE.value,
            LegalStatus.APPLICATION_PENDING.value,
            0,
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence))
            == 0
        )


def test_route_dto_command_result_and_permission_are_exact() -> None:
    route = _route()
    payload_type = _payload_type()
    adapter = _adapter()
    command_type = adapter.RecordAcceptanceNoticeCommand
    result_type = adapter.RecordAcceptanceNoticeResult

    assert route.status_code == 200
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert next(
        item.call for item in route.dependant.dependencies if item.name == "current_user"
    ) is get_current_user
    assert tuple(payload_type.model_fields) == REQUEST_FIELDS
    assert payload_type.model_config["extra"] == "forbid"
    assert payload_type.model_fields["occurred_at"].default is None
    assert payload_type.model_validate(_request_data()).model_dump() == {
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "effective_at": EFFECTIVE_AT,
        "occurred_at": None,
        "idempotency_key": "acceptance-notice-1",
    }
    assert is_dataclass(command_type) and command_type.__dataclass_params__.frozen
    assert is_dataclass(result_type) and result_type.__dataclass_params__.frozen
    assert tuple(item.name for item in fields(command_type)) == COMMAND_FIELDS
    assert tuple(item.name for item in fields(result_type)) == RESULT_FIELDS
    assert route.response_model is result_type


@pytest.mark.parametrize(
    "invalid",
    (
        {key: value for key, value in _request_data().items() if key != "evidence_version_id"},
        {key: value for key, value in _request_data().items() if key != "effective_at"},
        {key: value for key, value in _request_data().items() if key != "idempotency_key"},
        {**_request_data(), "case_id": CASE_ID},
        {**_request_data(), "document_id": DOCUMENT_ID},
        {**_request_data(), "actor_id": "client-actor"},
        {**_request_data(), "event_type": "ACCEPTANCE_NOTICE_RECORDED"},
        {**_request_data(), "reviewer_id": REVIEWER_ID},
        {**_request_data(), "evidence_kind": "ACCEPTANCE_NOTICE"},
        {**_request_data(), "confirmation_status": "CONFIRMED"},
        {**_request_data(), "payload": {}},
        {**_request_data(), "evidence_version_id": ""},
        {**_request_data(), "evidence_version_id": " evidence"},
        {**_request_data(), "evidence_version_id": "e" * 37},
        {**_request_data(), "idempotency_key": ""},
        {**_request_data(), "idempotency_key": "key "},
        {**_request_data(), "idempotency_key": "k" * 129},
        {**_request_data(), "evidence_version_id": 1},
        {**_request_data(), "effective_at": "not-a-datetime"},
        {**_request_data(), "effective_at": "2026-07-24T15:00:00+08:00"},
        {**_request_data(), "occurred_at": "2026-07-24T14:55:00+08:00"},
    ),
)
def test_invalid_request_shape_uses_existing_422_envelope(invalid: dict[str, object]) -> None:
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


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("evidence_version_id", StringSubclass(EVIDENCE_VERSION_ID)),
        ("idempotency_key", StringSubclass("acceptance-notice-1")),
        ("effective_at", DatetimeSubclass(2026, 7, 24, 15, 0)),
        ("occurred_at", DatetimeSubclass(2026, 7, 24, 14, 55)),
        ("effective_at", datetime(2026, 7, 24, 15, 0, tzinfo=timezone.utc)),
        ("occurred_at", datetime(2026, 7, 24, 14, 55, tzinfo=timezone.utc)),
    ),
)
def test_direct_dto_rejects_subclasses_and_aware_times(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        _payload_type().model_validate({**_request_data(), field: value})


@pytest.mark.parametrize("document_id", (" document", "document ", "x" * 37))
def test_path_document_id_is_exact_422(document_id: str) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: object()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(PATH.format(document_id=document_id), json=_request_data())
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_source_constructs_one_exact_empty_payload_event(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid(session_factory)
    adapter = _adapter()
    captured: list[LifecycleEventCommand] = []

    def apply(command: LifecycleEventCommand, _transaction: Session) -> LifecycleTransitionResult:
        captured.append(command)
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-acceptance-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="ACCEPTANCE_NOTICE_RECORDED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=WAITING_PROJECTION,
            current_projection=ACCEPTED_PROJECTION,
            legacy_case_status="ACCEPTED",
            idempotency_key=command.idempotency_key,
            reused=False,
        )

    monkeypatch.setattr(adapter, "apply_lifecycle_event", apply)
    command = adapter.RecordAcceptanceNoticeCommand(
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        actor_id="actor-acceptance-api",
        effective_at=EFFECTIVE_AT,
        occurred_at=OCCURRED_AT,
        idempotency_key="acceptance-notice-1",
    )
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        result = adapter.record_acceptance_notice_from_evidence(command, recording)

    assert result == adapter.RecordAcceptanceNoticeResult(
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        activity_id="activity-acceptance-api",
        activity_sequence=1,
        lifecycle_revision=1,
        effective_at=EFFECTIVE_AT,
        occurred_at=OCCURRED_AT,
        idempotency_key="acceptance-notice-1",
        reused=False,
    )
    assert captured == [
        LifecycleEventCommand(
            case_id=CASE_ID,
            event_type="ACCEPTANCE_NOTICE_RECORDED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=EFFECTIVE_AT,
            occurred_at=OCCURRED_AT,
            evidence_refs=(
                EvidenceReference(
                    case_id=CASE_ID,
                    evidence_kind="ACCEPTANCE_NOTICE",
                    object_type="DocumentEvidenceVersion",
                    object_id=EVIDENCE_VERSION_ID,
                    content_hash=CONTENT_HASH,
                    captured_at=REVIEWED_AT,
                ),
            ),
            actor_id="actor-acceptance-api",
            reviewer_id=None,
            idempotency_key="acceptance-notice-1",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        )
    ]
    assert recording.commit_calls == 0
    assert recording.rollback_calls == 0
    assert recording.close_calls == 0


@pytest.mark.parametrize(
    "semantics",
    (
        "out",
        "missing_template",
        "reference_only",
        "different_executable",
        "ambiguous",
        "invalid",
    ),
)
def test_non_acceptance_document_semantics_are_409_without_dispatch(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    semantics: str,
) -> None:
    _seed_valid(session_factory)
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        template = transaction.get(DocTemplate, "template-acceptance-api")
        assert document is not None and template is not None
        if semantics == "out":
            document.direction = "OUT"
        elif semantics == "missing_template":
            document.doc_template_id = None
        elif semantics == "reference_only":
            template.code = "REFERENCE_ONLY_ACCEPTANCE"
            template.input_fields = None
            template.status_effect = None
        elif semantics == "different_executable":
            template.status_effect = "OA1"
            template.deadline_template_code = "OA_REPLY"
            template.need_reply = True
            template.input_fields = (
                '{"catalog_kind":"OFFICIAL_NOTICE",'
                '"catalog_status":"EXECUTABLE",'
                '"execution_behavior":"OA_REPLY",'
                '"canonical_template_code":"OA_IN",'
                '"completion_event":"OFFICIAL_RECEIPT_ARCHIVED",'
                '"archive_status_restore":"SUB_EXAM",'
                '"deadline_source_policy":"EXPLICIT_OFFICIAL_DUE_REQUIRED"}'
            )
            resolved = resolve_document_semantics(template)
            assert resolved.catalog_status == "EXECUTABLE"
            assert resolved.execution_behavior == "OA_REPLY"
        elif semantics == "ambiguous":
            template.status_effect = "OA1"
        else:
            template.input_fields = "{not-json"
        transaction.commit()

    calls = 0

    def apply(*_args: object) -> None:
        nonlocal calls
        calls += 1

    adapter = _adapter()
    monkeypatch.setattr(adapter, "apply_lifecycle_event", apply)
    command = adapter.RecordAcceptanceNoticeCommand(
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        actor_id="actor-acceptance-api",
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        idempotency_key="acceptance-notice-1",
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_acceptance_notice_from_evidence(command, transaction)
    assert exc_info.value.status_code == 409
    assert calls == 0
    _assert_no_acceptance_write(session_factory)

@pytest.mark.parametrize(
    "conflict",
    (
        "non_current",
        "wrong_role",
        "non_final",
        "non_approved",
        "missing_reviewer",
        "self_review",
        "missing_reviewed_at",
        "malformed_hash",
        "malformed_lineage",
    ),
)
def test_invalid_persisted_evidence_is_409_without_dispatch(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    conflict: str,
) -> None:
    _seed_valid(session_factory)
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert version is not None
        if conflict == "non_current":
            version.current_identity_key = None
        elif conflict == "wrong_role":
            version.role = "OFFICIAL_NOTICE"
        elif conflict == "non_final":
            version.state = "DRAFT"
        elif conflict == "non_approved":
            version.review_state = "PENDING"
        elif conflict == "missing_reviewer":
            version.reviewer_id = None
        elif conflict == "self_review":
            version.reviewer_id = version.creator_id
        elif conflict == "missing_reviewed_at":
            version.reviewed_at = None
        elif conflict == "malformed_hash":
            version.content_hash = "sha256:not-canonical"
        else:
            version.lineage_key = " acceptance"
        transaction.commit()

    adapter = _adapter()
    monkeypatch.setattr(
        adapter,
        "apply_lifecycle_event",
        lambda *_args: pytest.fail("invalid evidence must not dispatch"),
    )
    command = adapter.RecordAcceptanceNoticeCommand(
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        actor_id="actor-acceptance-api",
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        idempotency_key="acceptance-notice-1",
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_acceptance_notice_from_evidence(command, transaction)
    assert exc_info.value.status_code == 409
    _assert_no_acceptance_write(session_factory)


def test_aware_stored_review_time_is_409_without_dispatch(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid(session_factory)
    adapter = _adapter()
    monkeypatch.setattr(
        adapter,
        "apply_lifecycle_event",
        lambda *_args: pytest.fail("aware review time must not dispatch"),
    )
    command = adapter.RecordAcceptanceNoticeCommand(
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        actor_id="actor-acceptance-api",
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        idempotency_key="acceptance-notice-1",
    )
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert version is not None
        version.reviewed_at = datetime(2026, 7, 24, 14, 30, tzinfo=timezone.utc)
        with pytest.raises(BusinessError) as exc_info:
            adapter.record_acceptance_notice_from_evidence(command, transaction)
    assert exc_info.value.status_code == 409
    _assert_no_acceptance_write(session_factory)


@pytest.mark.parametrize("relationship", ("other_document", "other_case"))
def test_cross_document_or_case_evidence_is_400(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    relationship: str,
) -> None:
    _seed_valid(session_factory)
    _add_other_evidence(session_factory, relationship=relationship)
    relation = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID),
    )
    assert relation.status_code == 400
    _assert_no_acceptance_write(session_factory)


def test_missing_resources_are_404(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_valid(session_factory)
    missing_document = client.post(
        PATH.format(document_id="missing-document"),
        headers=auth_headers,
        json=_request_data(),
    )
    missing_evidence = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(evidence_version_id="missing-evidence"),
    )
    assert missing_document.status_code == 404
    assert missing_evidence.status_code == 404
    _assert_no_acceptance_write(session_factory)


def test_api_uses_authenticated_actor_commits_once_and_returns_exact_result(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid(session_factory)
    actor_id = _actor_id(session_factory)
    adapter = _adapter()
    captured: list[object] = []
    result = adapter.RecordAcceptanceNoticeResult(
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        activity_id="activity-acceptance-api",
        activity_sequence=1,
        lifecycle_revision=1,
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        idempotency_key="acceptance-notice-1",
        reused=False,
    )

    def service(command: object, _transaction: object) -> object:
        captured.append(command)
        return result

    monkeypatch.setattr(documents_api, "record_acceptance_notice_from_evidence", service)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        with _client_for(recording) as client:
            response = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=_request_data(),
            )
    assert response.status_code == 200
    assert tuple(response.json()) == RESULT_FIELDS
    assert captured[0].actor_id == actor_id
    assert recording.commit_calls == 1
    assert recording.rollback_calls == 0
    assert recording.close_calls == 0


def test_fresh_and_identical_replay_persist_one_activity_and_reference(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_valid(session_factory)
    fresh = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    replay = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    assert fresh.status_code == replay.status_code == 200
    assert fresh.json()["reused"] is False
    assert replay.json() == {**fresh.json(), "reused": True}
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
        assert case.status == "ACCEPTED"
        assert case.official_procedure_stage == OfficialProcedureStage.ACCEPTED.value
        assert case.lifecycle_revision == 1
        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == CASE_ID)
        ).all()
        references = transaction.scalars(select(CaseActivityEventEvidence)).all()
        assert len(activities) == len(references) == 1
        assert (
            references[0].evidence_kind,
            references[0].object_type,
            references[0].object_id,
            references[0].content_hash,
            references[0].captured_at,
        ) == (
            "ACCEPTANCE_NOTICE",
            "DocumentEvidenceVersion",
            EVIDENCE_VERSION_ID,
            CONTENT_HASH,
            REVIEWED_AT,
        )


@pytest.mark.parametrize(
    "changed",
    ("document", "evidence", "content_hash", "reviewed_at", "effective_at", "occurred_at"),
)
def test_same_key_changed_bound_fact_is_409_and_write_free(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    changed: str,
) -> None:
    _seed_valid(session_factory)
    if changed == "document":
        _add_other_evidence(session_factory)
    else:
        _add_alternate_same_document_evidence(session_factory)
    first = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    target_document_id = DOCUMENT_ID
    if changed == "document":
        target_document_id = OTHER_DOCUMENT_ID
        payload = _request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID)
    elif changed == "evidence":
        payload = _request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID)
    elif changed in {"content_hash", "reviewed_at"}:
        with session_factory() as transaction:
            version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
            assert version is not None
            if changed == "content_hash":
                version.content_hash = f"sha256:{'b' * 64}"
            else:
                version.reviewed_at = datetime(2026, 7, 24, 14, 31)
            transaction.commit()
        payload = _request_data()
    elif changed == "effective_at":
        payload = _request_data(effective_at="2026-07-24T15:01:00")
    else:
        payload = _request_data(occurred_at="2026-07-24T14:55:00")
    drift = client.post(
        PATH.format(document_id=target_document_id),
        headers=auth_headers,
        json=payload,
    )
    assert first.status_code == 200
    assert drift.status_code == 409
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None and case.lifecycle_revision == 1
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 1
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence))
            == 1
        )


def test_same_key_changed_actor_is_409_without_second_write(
    session_factory: sessionmaker,
) -> None:
    _seed_valid(session_factory)
    adapter = _adapter()
    first = adapter.RecordAcceptanceNoticeCommand(
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        actor_id="actor-acceptance-one",
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        idempotency_key="acceptance-notice-actor-drift",
    )
    with session_factory() as transaction:
        adapter.record_acceptance_notice_from_evidence(first, transaction)
        transaction.commit()
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_acceptance_notice_from_evidence(
            replace(first, actor_id="actor-acceptance-two"),
            transaction,
        )
    assert exc_info.value.status_code == 409
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None and case.lifecycle_revision == 1
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 1


def test_different_key_after_projection_is_409_without_second_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_valid(session_factory)
    first = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    second = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(idempotency_key="acceptance-notice-2"),
    )
    assert first.status_code == 200
    assert second.status_code == 409
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None and case.lifecycle_revision == 1
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 1


def test_authentication_and_doc_edit_permission_preserve_401_and_403(
    client: TestClient,
    session_factory: sessionmaker,
) -> None:
    unauthenticated = client.post(PATH.format(document_id=DOCUMENT_ID), json=_request_data())
    assert unauthenticated.status_code == 401
    user_id = "acceptance-no-permission"
    with session_factory() as transaction:
        transaction.add(
            T_User(
                id=user_id,
                username="acceptance-no-permission",
                display_name="无权限用户",
                password_hash="unused",
                is_active=True,
            )
        )
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
    assert forbidden.json()["error"]["details"] == {"required_perm": "Doc.Edit"}


def test_lifecycle_failure_rolls_back_and_preserves_source_rows(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid(session_factory)
    adapter = _adapter()

    def fail(command: LifecycleEventCommand, transaction: Session) -> None:
        case = transaction.get(Case, command.case_id)
        document = transaction.get(Document, DOCUMENT_ID)
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert case is not None and document is not None and version is not None
        case.status = "ACCEPTED"
        document.title = "mutated"
        version.content_hash = f"sha256:{'b' * 64}"
        transaction.flush()
        raise BusinessError(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "injected lifecycle failure",
            status_code=409,
        )

    monkeypatch.setattr(adapter, "apply_lifecycle_event", fail)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        with _client_for(recording) as client:
            response = client.post(
                PATH.format(document_id=DOCUMENT_ID),
                headers=auth_headers,
                json=_request_data(),
            )
    assert response.status_code == 409
    assert recording.commit_calls == 0
    assert recording.rollback_calls == 1
    assert recording.close_calls == 0
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert document is not None and document.title == "受理通知书"
        assert version is not None and version.content_hash == CONTENT_HASH
    _assert_no_acceptance_write(session_factory)
