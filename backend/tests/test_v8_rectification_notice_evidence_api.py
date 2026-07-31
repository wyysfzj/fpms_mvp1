from __future__ import annotations

import inspect
import json
from contextlib import nullcontext
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
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

PATH = "/api/v1/documents/{document_id}/lifecycle/rectification-notice"
ROUTER_PATH = "/documents/{document_id}/lifecycle/rectification-notice"
CASE_ID = "case-rectification-api"
DOCUMENT_ID = "document-rectification-api"
ATTACHMENT_ID = "attachment-rectification-api"
EVIDENCE_VERSION_ID = "evidence-rectification-api"
ALT_ATTACHMENT_ID = "attachment-rectification-alt"
ALT_EVIDENCE_VERSION_ID = "evidence-rectification-alt"
OTHER_CASE_ID = "case-rectification-other"
OTHER_DOCUMENT_ID = "document-rectification-other"
OTHER_ATTACHMENT_ID = "attachment-rectification-other"
OTHER_EVIDENCE_VERSION_ID = "evidence-rectification-other"
ACTOR_USERNAME = "admin"
CREATOR_ID = "rectification-creator"
REVIEWER_ID = "rectification-reviewer"
EFFECTIVE_AT = datetime(2026, 7, 22, 14, 30)
OCCURRED_AT = datetime(2026, 7, 22, 14, 15)
REVIEWED_AT = datetime(2026, 7, 22, 13, 45)
OFFICIAL_DUE_DATE = date(2026, 8, 31)
CONTENT_HASH = f"sha256:{'d' * 64}"
ADAPTER_MODULE = "app.modules.documents.lifecycle_evidence_adapters"

PRELIMINARY_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
RECTIFICATION_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.RECTIFICATION_RESPONSE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
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
RESPONSE_FIELDS = (
    "case_id",
    "document_id",
    "evidence_version_id",
    "activity_id",
    "activity_sequence",
    "lifecycle_revision",
    "official_due_date",
    "official_due_date_source",
    "official_due_date_status",
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
        self.no_autoflush_enters = 0

    def __getattr__(self, name: str) -> object:
        return getattr(self.transaction, name)

    @property
    def no_autoflush(self):
        self.no_autoflush_enters += 1
        return self.transaction.no_autoflush

    def commit(self) -> None:
        self.commit_calls += 1
        self.transaction.commit()

    def rollback(self) -> None:
        self.rollback_calls += 1
        self.transaction.rollback()


def _deadline_extra_data(
    *,
    due_date: str = "2026-08-31",
    source: str = "MANUAL_OFFICIAL_NOTICE",
    status: str = "CONFIRMED",
) -> str:
    return json.dumps(
        {
            "OfficialDueDate": due_date,
            "OfficialDueDateSource": source,
            "OfficialDueDateStatus": status,
            "description": "原始补正通知书载荷",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _request_data(
    *,
    evidence_version_id: str = EVIDENCE_VERSION_ID,
    effective_at: str = "2026-07-22T14:30:00",
    occurred_at: str | None = None,
    idempotency_key: str = "rectification-notice-1",
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


def _adapter_module():
    return import_module(ADAPTER_MODULE)


def _case(*, case_id: str = CASE_ID, case_no: str = "V8-RECTIFICATION-API") -> Case:
    return Case(
        id=case_id,
        case_no=case_no,
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="补正通知书证据 API 测试案件",
        status="PRELIM_EXAM",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.PRELIMINARY_EXAMINATION.value,
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
    extra_data: str | None = None,
) -> DocumentEvidenceVersion:
    transaction.add(
        Document(
            id=document_id,
            case_id=case_id,
            direction="IN",
            extra_data=_deadline_extra_data() if extra_data is None else extra_data,
        )
    )
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
            lineage_key="rectification-notice",
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
                    file_name="rectification-alt.pdf",
                    file_path="/evidence/rectification-alt.pdf",
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
                    lineage_key="rectification-notice-alt",
                    role="OFFICIAL_FINAL_PDF",
                    version_number=1,
                    state="FINAL",
                    creator_id=CREATOR_ID,
                    review_state="APPROVED",
                    reviewer_id=REVIEWER_ID,
                    reviewed_at=REVIEWED_AT,
                    content_hash=CONTENT_HASH,
                    current_identity_key=f"{CASE_ID}|rectification-notice-alt",
                )
            )
        elif relationship in {"other_document", "other_case"}:
            case_id = CASE_ID
            if relationship == "other_case":
                case_id = OTHER_CASE_ID
                transaction.add(_case(case_id=case_id, case_no="V8-RECTIFICATION-OTHER"))
                transaction.flush()
            _add_document_evidence(
                transaction,
                case_id=case_id,
                document_id=OTHER_DOCUMENT_ID,
                attachment_id=OTHER_ATTACHMENT_ID,
                evidence_version_id=OTHER_EVIDENCE_VERSION_ID,
                lineage_key="rectification-notice-other",
            )
        else:
            raise AssertionError(f"unknown relationship fixture: {relationship}")
        transaction.commit()


def _authenticated_actor_id(session_factory: sessionmaker) -> str:
    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == ACTOR_USERNAME))
    assert actor_id is not None
    return actor_id


def _client_for_transaction(transaction: object) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    return TestClient(app)


def _assert_no_activity(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None
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
            0,
        )
        assert (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == CASE_ID)
            )
            == 0
        )


def test_route_dto_command_and_result_are_exact() -> None:
    route = _route()
    adapter = _adapter_module()

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

    payload_type = _payload_type()
    assert tuple(payload_type.model_fields) == REQUEST_FIELDS
    assert payload_type.model_config["extra"] == "forbid"
    assert payload_type.model_fields["occurred_at"].default is None
    assert payload_type.model_validate(_request_data()).model_dump() == {
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "effective_at": EFFECTIVE_AT,
        "occurred_at": None,
        "idempotency_key": "rectification-notice-1",
    }

    command_type = adapter.RecordRectificationNoticeCommand
    result_type = adapter.RecordRectificationNoticeResult
    assert is_dataclass(command_type) and command_type.__dataclass_params__.frozen
    assert is_dataclass(result_type) and result_type.__dataclass_params__.frozen
    assert tuple(field.name for field in fields(command_type)) == COMMAND_FIELDS
    assert tuple(field.name for field in fields(result_type)) == RESPONSE_FIELDS
    assert route.response_model is result_type
    assert get_type_hints(result_type) == {
        "case_id": str,
        "document_id": str,
        "evidence_version_id": str,
        "activity_id": str,
        "activity_sequence": int,
        "lifecycle_revision": int,
        "official_due_date": date,
        "official_due_date_source": str,
        "official_due_date_status": str,
        "idempotency_key": str,
        "reused": bool,
    }


@pytest.mark.parametrize(
    "invalid",
    (
        {key: value for key, value in _request_data().items() if key != "evidence_version_id"},
        {key: value for key, value in _request_data().items() if key != "effective_at"},
        {key: value for key, value in _request_data().items() if key != "idempotency_key"},
        {**_request_data(), "unexpected": True},
        {**_request_data(), "OfficialDueDate": "2026-08-31"},
        {**_request_data(), "actor_id": "client-actor"},
        {**_request_data(), "evidence_version_id": ""},
        {**_request_data(), "evidence_version_id": " evidence"},
        {**_request_data(), "evidence_version_id": "e" * 37},
        {**_request_data(), "idempotency_key": ""},
        {**_request_data(), "idempotency_key": "key "},
        {**_request_data(), "idempotency_key": "k" * 129},
        {**_request_data(), "evidence_version_id": 1},
        {**_request_data(), "idempotency_key": 1},
        {**_request_data(), "effective_at": "not-a-datetime"},
        {**_request_data(), "effective_at": "2026-07-22T14:30:00+08:00"},
        {**_request_data(), "occurred_at": "2026-07-22T14:15:00+08:00"},
    ),
)
def test_invalid_wire_inputs_use_existing_422_envelope(invalid: dict[str, object]) -> None:
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
        ("idempotency_key", StringSubclass("rectification-notice-1")),
        ("effective_at", DatetimeSubclass(2026, 7, 22, 14, 30)),
        ("occurred_at", DatetimeSubclass(2026, 7, 22, 14, 15)),
        ("effective_at", datetime(2026, 7, 22, 14, 30, tzinfo=timezone.utc)),
        ("occurred_at", datetime(2026, 7, 22, 14, 15, tzinfo=timezone.utc)),
    ),
)
def test_direct_dto_rejects_subclasses_and_aware_times(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        _payload_type().model_validate({**_request_data(), field: value})


def test_valid_request_maps_only_exact_event_and_commits_once(
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
            activity_id="activity-rectification-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="RECTIFICATION_NOTICE_RECORDED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=PRELIMINARY_PROJECTION,
            current_projection=RECTIFICATION_PROJECTION,
            legacy_case_status="AMENDMENT",
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
                json=_request_data(occurred_at="2026-07-22T14:15:00"),
            )

    assert response.status_code == 200
    assert tuple(response.json()) == RESPONSE_FIELDS
    assert response.json() == {
        "case_id": CASE_ID,
        "document_id": DOCUMENT_ID,
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "activity_id": "activity-rectification-api",
        "activity_sequence": 1,
        "lifecycle_revision": 1,
        "official_due_date": "2026-08-31",
        "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
        "official_due_date_status": "CONFIRMED",
        "idempotency_key": "rectification-notice-1",
        "reused": False,
    }
    assert captured == [
        LifecycleEventCommand(
            case_id=CASE_ID,
            event_type="RECTIFICATION_NOTICE_RECORDED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=EFFECTIVE_AT,
            occurred_at=OCCURRED_AT,
            evidence_refs=(
                EvidenceReference(
                    case_id=CASE_ID,
                    evidence_kind="RECTIFICATION_NOTICE",
                    object_type="DocumentEvidenceVersion",
                    object_id=EVIDENCE_VERSION_ID,
                    content_hash=CONTENT_HASH,
                    captured_at=REVIEWED_AT,
                ),
            ),
            actor_id=actor_id,
            reviewer_id=None,
            idempotency_key="rectification-notice-1",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "official_due_date": "2026-08-31",
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
            },
        )
    ]
    assert recording.no_autoflush_enters == 1
    assert recording.commit_calls == 1
    assert recording.rollback_calls == 0


@pytest.mark.parametrize("occurred_at", (None, "2026-07-22T14:15:00"))
def test_fresh_and_identical_replay_persist_one_exact_activity(
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
                PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=payload
            )
            replay = client.post(
                PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=payload
            )

    assert fresh.status_code == replay.status_code == 200
    assert fresh.json()["reused"] is False
    assert replay.json() == {**fresh.json(), "reused": True}
    assert recording.commit_calls == 2
    assert recording.rollback_calls == 0

    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        document = transaction.get(Document, DOCUMENT_ID)
        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == CASE_ID)
        ).all()
        assert case is not None and document is not None
        assert len(activities) == 1
        activity = activities[0]
        assert (
            activity.activity_type,
            activity.lane,
            activity.confirmation_status,
            activity.old_official_procedure_stage,
            activity.new_official_procedure_stage,
            activity.effective_at,
            activity.occurred_at,
            json.loads(activity.payload_json),
        ) == (
            "RECTIFICATION_NOTICE_RECORDED",
            ActivityLane.LIFECYCLE.value,
            ConfirmationStatus.CONFIRMED.value,
            OfficialProcedureStage.PRELIMINARY_EXAMINATION.value,
            OfficialProcedureStage.RECTIFICATION_RESPONSE.value,
            EFFECTIVE_AT,
            None if occurred_at is None else OCCURRED_AT,
            {
                "official_due_date": "2026-08-31",
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
            },
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
                "RECTIFICATION_NOTICE",
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
            "AMENDMENT",
            BusinessStage.OA_REPLY_IN_PROGRESS.value,
            OfficialProcedureStage.RECTIFICATION_RESPONSE.value,
            LegalStatus.APPLICATION_PENDING.value,
            1,
        )
        assert document.extra_data == _deadline_extra_data()


@pytest.mark.parametrize(
    "extra_data",
    (
        None,
        "legacy deadline text",
        json.dumps({"OfficialDueDate": "2026-08-31"}),
        json.dumps(
            {
                "OfficialDueDate": "2026-08-31",
                "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                "OfficialDueDateStatus": "NEEDS_CONFIRMATION",
            }
        ),
        json.dumps(
            {
                "OfficialDueDate": "2026-8-31",
                "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                "OfficialDueDateStatus": "CONFIRMED",
            }
        ),
        json.dumps(
            {
                "OfficialDueDate": "2026-08-31",
                "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            }
        ),
    ),
)
def test_unconfirmed_partial_legacy_or_malformed_deadline_is_exact_409(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    extra_data: str | None,
) -> None:
    _seed_valid_evidence(session_factory)
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        document.extra_data = extra_data
        transaction.commit()

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=_request_data()
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RECTIFICATION_NOTICE_DEADLINE_CONFLICT"
    assert response.json()["error"]["details"] == {"field": "OfficialDueDate"}
    _assert_no_activity(session_factory)


@pytest.mark.parametrize("relationship", ("other_document", "other_case"))
def test_cross_document_or_case_evidence_is_exact_400(
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
    assert response.json()["error"]["code"] == (
        "RECTIFICATION_NOTICE_EVIDENCE_RELATION_MISMATCH"
    )
    assert response.json()["error"]["details"] == {"field": "evidence_version_id"}
    _assert_no_activity(session_factory)


def _invalidate_evidence(version: DocumentEvidenceVersion, conflict: str) -> None:
    if conflict == "non_current":
        version.current_identity_key = None
    elif conflict == "non_final":
        version.state = "DRAFT"
    elif conflict == "non_approved":
        version.review_state = "PENDING"
    elif conflict == "wrong_role":
        version.role = "OFFICIAL_NOTICE"
    elif conflict == "missing_reviewer":
        version.reviewer_id = None
    elif conflict == "self_review":
        version.reviewer_id = version.creator_id
    elif conflict == "missing_review_time":
        version.reviewed_at = None
    elif conflict == "malformed_hash":
        version.content_hash = "sha256:not-canonical"
    elif conflict == "whitespace_creator":
        version.creator_id = f" {version.creator_id}"
    elif conflict == "whitespace_reviewer":
        version.reviewer_id = f"{version.reviewer_id} "
    elif conflict == "zero_version":
        version.version_number = 0
    elif conflict == "negative_version":
        version.version_number = -1
    elif conflict == "malformed_attachment_id":
        version.attachment_id = "x" * 37
    else:
        raise AssertionError(f"unknown evidence conflict fixture: {conflict}")


@pytest.mark.parametrize(
    "conflict",
    (
        "non_current",
        "non_final",
        "non_approved",
        "wrong_role",
        "missing_reviewer",
        "self_review",
        "missing_review_time",
        "malformed_hash",
        "whitespace_creator",
        "whitespace_reviewer",
        "zero_version",
        "negative_version",
        "malformed_attachment_id",
    ),
)
def test_invalid_evidence_state_is_exact_409(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    conflict: str,
) -> None:
    _seed_valid_evidence(session_factory)
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert version is not None
        if conflict == "malformed_attachment_id":
            transaction.add(
                DocAttachment(
                    id="x" * 37,
                    document_id=DOCUMENT_ID,
                    file_name="malformed-attachment-id.pdf",
                    file_path="/evidence/malformed-attachment-id.pdf",
                    mime_type="application/pdf",
                    content_hash=CONTENT_HASH,
                )
            )
            transaction.flush()
        _invalidate_evidence(version, conflict)
        transaction.commit()

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=_request_data()
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RECTIFICATION_NOTICE_EVIDENCE_CONFLICT"
    assert response.json()["error"]["details"] == {"field": "evidence_version_id"}
    _assert_no_activity(session_factory)


@pytest.mark.parametrize(
    ("missing", "code"),
    (("document", "DOCUMENT_NOT_FOUND"), ("evidence", "EVIDENCE_VERSION_NOT_FOUND")),
)
def test_missing_document_or_evidence_preserves_specific_404(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    missing: str,
    code: str,
) -> None:
    if missing == "evidence":
        _seed_valid_evidence(session_factory)
    response = client.post(
        PATH.format(document_id="missing-document" if missing == "document" else DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(evidence_version_id="missing-evidence"),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == code
    if missing == "evidence":
        _assert_no_activity(session_factory)


def test_missing_case_is_specific_404_before_lifecycle_delegation() -> None:
    adapter = _adapter_module()
    document = Document(
        id=DOCUMENT_ID,
        case_id=CASE_ID,
        direction="IN",
        extra_data=_deadline_extra_data(),
    )

    class MissingCaseSession:
        no_autoflush = nullcontext()

        def get(self, model: object, identity: str) -> object | None:
            if model is Document and identity == DOCUMENT_ID:
                return document
            if model is Case and identity == CASE_ID:
                return None
            raise AssertionError("evidence lookup must not run after missing case")

    with pytest.raises(BusinessError) as exc_info:
        adapter.record_rectification_notice_from_evidence(
            adapter.RecordRectificationNoticeCommand(
                document_id=DOCUMENT_ID,
                evidence_version_id=EVIDENCE_VERSION_ID,
                actor_id="actor-rectification",
                effective_at=EFFECTIVE_AT,
                occurred_at=None,
                idempotency_key="rectification-notice-1",
            ),
            MissingCaseSession(),
        )

    assert (exc_info.value.status_code, exc_info.value.code) == (404, "CASE_NOT_FOUND")


@pytest.mark.parametrize("changed", ("effective_at", "occurred_at", "evidence", "deadline"))
def test_same_key_with_any_changed_bound_fact_is_idempotency_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    changed: str,
) -> None:
    _seed_valid_evidence(session_factory)
    _add_alternate_evidence(session_factory)
    first = client.post(
        PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=_request_data()
    )
    changed_payload = _request_data()
    if changed == "effective_at":
        changed_payload = _request_data(effective_at="2026-07-22T14:31:00")
    elif changed == "occurred_at":
        changed_payload = _request_data(occurred_at="2026-07-22T14:15:00")
    elif changed == "evidence":
        changed_payload = _request_data(evidence_version_id=ALT_EVIDENCE_VERSION_ID)
    elif changed == "deadline":
        with session_factory() as transaction:
            document = transaction.get(Document, DOCUMENT_ID)
            assert document is not None
            document.extra_data = _deadline_extra_data(due_date="2026-09-01")
            transaction.commit()

    response = client.post(
        PATH.format(document_id=DOCUMENT_ID), headers=auth_headers, json=changed_payload
    )

    assert first.status_code == 200
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None and case.lifecycle_revision == 1
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
        PATH.format(document_id=DOCUMENT_ID), json=_request_data()
    )
    assert unauthenticated.status_code == 401
    assert unauthenticated.json()["error"]["code"] == "AUTH_REQUIRED"

    user_id = "rectification-no-permission-user"
    with session_factory() as transaction:
        transaction.add(
            T_User(
                id=user_id,
                username="rectification-no-permission",
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
    assert forbidden.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Doc.Edit"},
        }
    }


def test_deeper_lifecycle_error_passes_through_and_rolls_back(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid_evidence(session_factory)

    def fail(command: LifecycleEventCommand, transaction: Session) -> None:
        case = transaction.get(Case, command.case_id)
        assert case is not None
        case.official_procedure_stage = OfficialProcedureStage.RECTIFICATION_RESPONSE.value
        transaction.flush()
        raise BusinessError(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "deeper lifecycle error",
            details={"marker": "rollback"},
            status_code=409,
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

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "LIFECYCLE_PROJECTION_CONFLICT",
            "message": "deeper lifecycle error",
            "details": {"marker": "rollback"},
        }
    }
    assert recording.commit_calls == 0
    assert recording.rollback_calls == 1
    _assert_no_activity(session_factory)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("document_id", ""),
        ("evidence_version_id", " evidence"),
        ("actor_id", "actor "),
        ("idempotency_key", "k" * 129),
        ("effective_at", DatetimeSubclass(2026, 7, 22, 14, 30)),
        ("occurred_at", datetime(2026, 7, 22, 14, 15, tzinfo=timezone.utc)),
    ),
)
def test_invalid_service_command_fails_before_transaction_access(
    field: str,
    value: object,
) -> None:
    adapter = _adapter_module()
    values = {
        "document_id": DOCUMENT_ID,
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "actor_id": "actor-rectification",
        "effective_at": EFFECTIVE_AT,
        "occurred_at": None,
        "idempotency_key": "rectification-notice-1",
    }
    values[field] = value

    class TransactionForbidden:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"invalid command must not access transaction.{name}")

    with pytest.raises(BusinessError) as exc_info:
        adapter.record_rectification_notice_from_evidence(
            adapter.RecordRectificationNoticeCommand(**values),
            TransactionForbidden(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == "LIFECYCLE_EVENT_INVALID"
    assert exc_info.value.details == {"field": field}
