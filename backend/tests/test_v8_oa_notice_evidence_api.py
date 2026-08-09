from __future__ import annotations

import inspect
import json
from dataclasses import fields, is_dataclass, replace
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
from app.modules.documents import official_notice_catalog
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)

PATH = "/api/v1/documents/{document_id}/lifecycle/oa-notice"
ROUTER_PATH = "/documents/{document_id}/lifecycle/oa-notice"
CASE_ID = "case-oa-notice-api"
DOCUMENT_ID = "document-oa-notice-api"
ATTACHMENT_ID = "attachment-oa-notice-api"
EVIDENCE_VERSION_ID = "evidence-oa-notice-api"
OTHER_CASE_ID = "case-oa-notice-other"
OTHER_DOCUMENT_ID = "document-oa-notice-other"
OTHER_ATTACHMENT_ID = "attachment-oa-other"
OTHER_EVIDENCE_VERSION_ID = "evidence-oa-notice-other"
ACTOR_USERNAME = "admin"
CREATOR_ID = "oa-notice-creator"
REVIEWER_ID = "oa-notice-reviewer"
EFFECTIVE_AT = datetime(2026, 7, 24, 16, 0)
OCCURRED_AT = datetime(2026, 7, 24, 15, 55)
REVIEWED_AT = datetime(2026, 7, 24, 15, 30)
OFFICIAL_DUE_DATE = date(2026, 10, 24)
CONTENT_HASH = f"sha256:{'c' * 64}"
ADAPTER_MODULE = "app.modules.documents.lifecycle_evidence_adapters"

SOURCE_SEQUENCE = {
    "OA_IN": 1,
    "OFFICIAL_NOTICE_003": 1,
    "OFFICIAL_NOTICE_005": 2,
    "OFFICIAL_NOTICE_021": 3,
    "OFFICIAL_NOTICE_024": 4,
    "OFFICIAL_NOTICE_029": 5,
}
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
    "official_due_date",
    "official_due_date_source",
    "official_due_date_status",
    "oa_sequence",
    "idempotency_key",
    "reused",
)

SUBSTANTIVE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
    official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
)
OA_RESPONSE_PROJECTION = LifecycleProjection(
    business_stage=BusinessStage.OA_REPLY_IN_PROGRESS,
    official_procedure_stage=OfficialProcedureStage.OFFICE_ACTION_RESPONSE,
    legal_status=LegalStatus.APPLICATION_PENDING,
    lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
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


def _deadline_extra_data(
    *,
    due_date: str = "2026-10-24",
    source: str = "MANUAL_OFFICIAL_NOTICE",
    status: str = "CONFIRMED",
) -> str:
    return json.dumps(
        {
            "OfficialDueDate": due_date,
            "OfficialDueDateSource": source,
            "OfficialDueDateStatus": status,
            "description": "原始审查意见通知载荷",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _request_data(
    *,
    evidence_version_id: str = EVIDENCE_VERSION_ID,
    effective_at: str = "2026-07-24T16:00:00",
    occurred_at: str | None = None,
    idempotency_key: str = "oa-notice-1",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "evidence_version_id": evidence_version_id,
        "effective_at": effective_at,
        "idempotency_key": idempotency_key,
    }
    if occurred_at is not None:
        payload["occurred_at"] = occurred_at
    return payload


def _case(
    *,
    case_id: str = CASE_ID,
    case_no: str = "V8-OA-NOTICE-API",
) -> Case:
    return Case(
        id=case_id,
        case_no=case_no,
        case_type="NORMAL",
        patent_category="INV",
        flow_dir="CN_DOMESTIC",
        title_cn="审查意见通知证据适配测试案件",
        status="SUB_EXAM",
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT.value,
        official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
        legal_status=LegalStatus.APPLICATION_PENDING.value,
        lifecycle_revision=0,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED.value,
    )


def _template(
    *,
    template_id: str = "template-oa-notice-api",
    code: str = "OA_IN",
) -> DocTemplate:
    sequence = SOURCE_SEQUENCE.get(code, 1)
    status_effect = "OA1" if sequence == 1 else "OA2"
    input_fields = None
    if code != "OA_IN":
        input_fields = json.dumps(
            {
                "archive_status_restore": "SUB_EXAM",
                "canonical_template_code": "OA_IN",
                "catalog_kind": "OFFICIAL_NOTICE",
                "catalog_status": "EXECUTABLE",
                "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED",
                "execution_behavior": "OA_REPLY",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    return DocTemplate(
        id=template_id,
        code=code,
        name="审查意见通知书",
        direction="IN",
        enabled=True,
        status_effect=status_effect,
        deadline_template_code="OA_REPLY" if sequence == 1 else "OA_REPLY_SUBSEQUENT",
        need_reply=True,
        input_fields=input_fields,
    )


def _document(
    *,
    document_id: str = DOCUMENT_ID,
    case_id: str = CASE_ID,
    template_id: str | None = "template-oa-notice-api",
    direction: str = "IN",
    extra_data: str | None = None,
) -> Document:
    return Document(
        id=document_id,
        case_id=case_id,
        doc_template_id=template_id,
        direction=direction,
        title="审查意见通知书",
        extra_data=_deadline_extra_data() if extra_data is None else extra_data,
    )


def _attachment(
    *,
    attachment_id: str = ATTACHMENT_ID,
    document_id: str = DOCUMENT_ID,
    content_hash: str = CONTENT_HASH,
) -> DocAttachment:
    return DocAttachment(
        id=attachment_id,
        document_id=document_id,
        file_name=f"{attachment_id}.pdf",
        file_path=f"/evidence/{attachment_id}.pdf",
        mime_type="application/pdf",
        content_hash=content_hash,
    )


def _version(
    *,
    version_id: str = EVIDENCE_VERSION_ID,
    case_id: str = CASE_ID,
    document_id: str = DOCUMENT_ID,
    attachment_id: str = ATTACHMENT_ID,
    lineage_key: str = "oa-notice-final",
    content_hash: str = CONTENT_HASH,
) -> DocumentEvidenceVersion:
    return DocumentEvidenceVersion(
        id=version_id,
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
        content_hash=content_hash,
        current_identity_key=f"{case_id}|{lineage_key}",
    )


def _seed_valid(
    session_factory: sessionmaker,
    *,
    template_code: str = "OA_IN",
) -> None:
    with session_factory() as transaction:
        transaction.add(_case())
        template = transaction.scalar(
            select(DocTemplate).where(DocTemplate.code == template_code)
        )
        if template is None:
            template = _template(code=template_code)
            transaction.add(template)
            transaction.flush()
        transaction.add(_document(template_id=template.id))
        transaction.flush()
        transaction.add(_attachment())
        transaction.flush()
        transaction.add(_version())
        transaction.commit()


def _add_other_evidence(
    session_factory: sessionmaker,
    *,
    other_case: bool = False,
    same_document: bool = False,
) -> None:
    with session_factory() as transaction:
        source_document = transaction.get(Document, DOCUMENT_ID)
        assert source_document is not None
        case_id = CASE_ID
        document_id = DOCUMENT_ID
        if other_case:
            transaction.add(_case(case_id=OTHER_CASE_ID, case_no="V8-OA-NOTICE-OTHER"))
            case_id = OTHER_CASE_ID
        if not same_document:
            document_id = OTHER_DOCUMENT_ID
            transaction.add(
                _document(
                    document_id=document_id,
                    case_id=case_id,
                    template_id=source_document.doc_template_id,
                )
            )
            transaction.flush()
        transaction.add(
            _attachment(
                attachment_id=OTHER_ATTACHMENT_ID,
                document_id=document_id,
            )
        )
        transaction.flush()
        transaction.add(
            _version(
                version_id=OTHER_EVIDENCE_VERSION_ID,
                case_id=case_id,
                document_id=document_id,
                attachment_id=OTHER_ATTACHMENT_ID,
                lineage_key="oa-notice-other",
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


def _assert_no_write(session_factory: sessionmaker) -> None:
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
            "SUB_EXAM",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            0,
        )
        assert document.extra_data == _deadline_extra_data()
        assert version.content_hash == CONTENT_HASH
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence))
            == 0
        )


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
            "SUB_EXAM",
            BusinessStage.PROSECUTION_MANAGEMENT.value,
            OfficialProcedureStage.SUBSTANTIVE_EXAMINATION.value,
            LegalStatus.APPLICATION_PENDING.value,
            0,
        )
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 0
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence))
            == 0
        )


def _command(**changes: object):
    adapter = _adapter()
    values = {
        "document_id": DOCUMENT_ID,
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "actor_id": "actor-oa-notice-api",
        "effective_at": EFFECTIVE_AT,
        "occurred_at": OCCURRED_AT,
        "idempotency_key": "oa-notice-1",
    }
    values.update(changes)
    return adapter.RecordOaNoticeCommand(**values)


def test_catalog_sequence_route_dto_result_and_permission_are_exact() -> None:
    resolver = official_notice_catalog.resolve_oa_notice_sequence
    assert {code: resolver(code) for code in SOURCE_SEQUENCE} == SOURCE_SEQUENCE
    for invalid in (
        None,
        1,
        "",
        " OA_IN",
        "OA_IN ",
        "oa_in",
        StringSubclass("OA_IN"),
        "OFFICIAL_NOTICE_004",
        "ACCEPTANCE_NOTICE",
    ):
        assert resolver(invalid) is None

    route = _route()
    payload_type = _payload_type()
    adapter = _adapter()
    command_type = adapter.RecordOaNoticeCommand
    result_type = adapter.RecordOaNoticeResult

    assert route.status_code == 200
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert next(
        item.call for item in route.dependant.dependencies if item.name == "current_user"
    ) is get_current_user
    assert next(item.call for item in route.dependant.dependencies if item.name == "db") is get_db
    assert tuple(payload_type.model_fields) == REQUEST_FIELDS
    assert payload_type.model_config["extra"] == "forbid"
    assert payload_type.model_fields["occurred_at"].default is None
    assert payload_type.model_validate(_request_data()).model_dump() == {
        "evidence_version_id": EVIDENCE_VERSION_ID,
        "effective_at": EFFECTIVE_AT,
        "occurred_at": None,
        "idempotency_key": "oa-notice-1",
    }
    assert is_dataclass(command_type) and command_type.__dataclass_params__.frozen
    assert is_dataclass(result_type) and result_type.__dataclass_params__.frozen
    assert tuple(item.name for item in fields(command_type)) == COMMAND_FIELDS
    assert tuple(item.name for item in fields(result_type)) == RESULT_FIELDS
    assert route.response_model is result_type
    assert get_type_hints(result_type) == {
        "case_id": str,
        "document_id": str,
        "evidence_version_id": str,
        "activity_id": str,
        "activity_sequence": int,
        "lifecycle_revision": int,
        "effective_at": datetime,
        "occurred_at": datetime | None,
        "official_due_date": date,
        "official_due_date_source": str,
        "official_due_date_status": str,
        "oa_sequence": int,
        "idempotency_key": str,
        "reused": bool,
    }


@pytest.mark.parametrize(
    "invalid",
    (
        {key: value for key, value in _request_data().items() if key != "evidence_version_id"},
        {key: value for key, value in _request_data().items() if key != "effective_at"},
        {key: value for key, value in _request_data().items() if key != "idempotency_key"},
        {**_request_data(), "case_id": CASE_ID},
        {**_request_data(), "document_id": DOCUMENT_ID},
        {**_request_data(), "actor_id": "client-actor"},
        {**_request_data(), "reviewer_id": REVIEWER_ID},
        {**_request_data(), "event_type": "OA_NOTICE_RECORDED"},
        {**_request_data(), "evidence_kind": "OA_NOTICE"},
        {**_request_data(), "official_due_date": "2026-10-24"},
        {**_request_data(), "oa_sequence": 1},
        {**_request_data(), "evidence_version_id": ""},
        {**_request_data(), "evidence_version_id": " evidence"},
        {**_request_data(), "evidence_version_id": "e" * 37},
        {**_request_data(), "idempotency_key": ""},
        {**_request_data(), "idempotency_key": "key "},
        {**_request_data(), "idempotency_key": "k" * 129},
        {**_request_data(), "evidence_version_id": 1},
        {**_request_data(), "idempotency_key": 1},
        {**_request_data(), "effective_at": "not-a-datetime"},
        {**_request_data(), "effective_at": "2026-07-24T16:00:00+08:00"},
        {**_request_data(), "occurred_at": "2026-07-24T15:55:00+08:00"},
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
        ("idempotency_key", StringSubclass("oa-notice-1")),
        ("effective_at", DatetimeSubclass(2026, 7, 24, 16, 0)),
        ("occurred_at", DatetimeSubclass(2026, 7, 24, 15, 55)),
        ("effective_at", datetime(2026, 7, 24, 16, 0, tzinfo=timezone.utc)),
        ("occurred_at", datetime(2026, 7, 24, 15, 55, tzinfo=timezone.utc)),
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


@pytest.mark.parametrize(("template_code", "oa_sequence"), SOURCE_SEQUENCE.items())
def test_each_authoritative_source_constructs_one_exact_event(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    template_code: str,
    oa_sequence: int,
) -> None:
    _seed_valid(session_factory, template_code=template_code)
    adapter = _adapter()
    captured: list[LifecycleEventCommand] = []

    def apply(command: LifecycleEventCommand, _transaction: Session) -> LifecycleTransitionResult:
        captured.append(command)
        return LifecycleTransitionResult(
            case_id=CASE_ID,
            activity_id="activity-oa-notice-api",
            sequence=1,
            lifecycle_revision=1,
            lane=ActivityLane.LIFECYCLE,
            event_type="OA_NOTICE_RECORDED",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            previous_projection=SUBSTANTIVE_PROJECTION,
            current_projection=OA_RESPONSE_PROJECTION,
            legacy_case_status="OA1" if oa_sequence == 1 else "OA2",
            idempotency_key=command.idempotency_key,
            reused=False,
        )

    monkeypatch.setattr(adapter, "apply_lifecycle_event", apply)
    with session_factory() as transaction:
        recording = RecordingSession(transaction)
        result = adapter.record_oa_notice_from_evidence(_command(), recording)

    assert result == adapter.RecordOaNoticeResult(
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        activity_id="activity-oa-notice-api",
        activity_sequence=1,
        lifecycle_revision=1,
        effective_at=EFFECTIVE_AT,
        occurred_at=OCCURRED_AT,
        official_due_date=OFFICIAL_DUE_DATE,
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
        oa_sequence=oa_sequence,
        idempotency_key="oa-notice-1",
        reused=False,
    )
    assert captured == [
        LifecycleEventCommand(
            case_id=CASE_ID,
            event_type="OA_NOTICE_RECORDED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=EFFECTIVE_AT,
            occurred_at=OCCURRED_AT,
            evidence_refs=(
                EvidenceReference(
                    case_id=CASE_ID,
                    evidence_kind="OA_NOTICE",
                    object_type="DocumentEvidenceVersion",
                    object_id=EVIDENCE_VERSION_ID,
                    content_hash=CONTENT_HASH,
                    captured_at=REVIEWED_AT,
                ),
            ),
            actor_id="actor-oa-notice-api",
            reviewer_id=None,
            idempotency_key="oa-notice-1",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "official_due_date": "2026-10-24",
                "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
                "official_due_date_status": "CONFIRMED",
                "oa_sequence": oa_sequence,
                "source_template_code": template_code,
            },
        )
    ]
    assert recording.no_autoflush_enters == 1
    assert recording.commit_calls == 0
    assert recording.rollback_calls == 0
    assert recording.close_calls == 0
    _assert_no_write(session_factory)

@pytest.mark.parametrize(
    "conflict",
    (
        "unlisted",
        "ambiguous",
        "disabled",
        "out",
        "non_executable",
        "different_executable",
        "mismatched_source",
        "missing_template",
    ),
)
def test_invalid_or_mismatched_source_fails_closed_without_dispatch(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    conflict: str,
) -> None:
    _seed_valid(session_factory, template_code="OFFICIAL_NOTICE_003")
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        template = transaction.get(DocTemplate, "template-oa-notice-api")
        assert document is not None and template is not None
        if conflict == "unlisted":
            template.code = "OFFICIAL_NOTICE_004"
        elif conflict == "ambiguous":
            template.input_fields = None
        elif conflict == "disabled":
            template.enabled = False
        elif conflict == "out":
            document.direction = "OUT"
        elif conflict == "non_executable":
            template.input_fields = json.dumps(
                {"catalog_kind": "OFFICIAL_NOTICE", "catalog_status": "REFERENCE_ONLY"}
            )
            template.status_effect = None
            template.deadline_template_code = None
            template.need_reply = False
        elif conflict == "different_executable":
            template.status_effect = "ACCEPTED"
            template.deadline_template_code = None
            template.need_reply = False
            template.input_fields = json.dumps(
                {
                    "canonical_template_code": "ACCEPTANCE_NOTICE",
                    "catalog_kind": "OFFICIAL_NOTICE",
                    "catalog_status": "EXECUTABLE",
                    "execution_behavior": "ACCEPTANCE_NOTICE",
                }
            )
        elif conflict == "mismatched_source":
            template.code = "OFFICIAL_NOTICE_005"
            template.status_effect = "OA1"
            template.deadline_template_code = "OA_REPLY"
        else:
            document.doc_template_id = None
        transaction.commit()

    adapter = _adapter()
    monkeypatch.setattr(
        adapter,
        "apply_lifecycle_event",
        lambda *_args: pytest.fail("invalid source must not dispatch"),
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_oa_notice_from_evidence(_command(), transaction)
    assert exc_info.value.status_code == (404 if conflict == "missing_template" else 409)
    _assert_no_write(session_factory)


@pytest.mark.parametrize(
    "extra_data",
    (
        None,
        "legacy deadline text",
        json.dumps({"OfficialDueDate": "2026-10-24"}),
        json.dumps(
            {
                "OfficialDueDate": "2026-10-24",
                "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                "OfficialDueDateStatus": "NEEDS_CONFIRMATION",
            }
        ),
        json.dumps(
            {
                "OfficialDueDate": "2026-10-24",
                "OfficialDueDateSource": "CALCULATED",
                "OfficialDueDateStatus": "CONFIRMED",
            }
        ),
        json.dumps(
            {
                "OfficialDueDate": "2026-1-24",
                "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
                "OfficialDueDateStatus": "CONFIRMED",
            }
        ),
    ),
)
def test_missing_partial_legacy_or_unconfirmed_due_tuple_is_409_without_dispatch(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    extra_data: str | None,
) -> None:
    _seed_valid(session_factory)
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        document.extra_data = extra_data
        transaction.commit()
    adapter = _adapter()
    monkeypatch.setattr(
        adapter,
        "apply_lifecycle_event",
        lambda *_args: pytest.fail("invalid due tuple must not dispatch"),
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_oa_notice_from_evidence(_command(), transaction)
    assert exc_info.value.status_code == 409
    _assert_no_activity(session_factory)


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
def test_invalid_evidence_is_409_without_dispatch(
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
            version.lineage_key = " oa-notice-final"
        transaction.commit()
    adapter = _adapter()
    monkeypatch.setattr(
        adapter,
        "apply_lifecycle_event",
        lambda *_args: pytest.fail("invalid evidence must not dispatch"),
    )
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_oa_notice_from_evidence(_command(), transaction)
    assert exc_info.value.status_code == 409
    _assert_no_activity(session_factory)


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
    with session_factory() as transaction:
        version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
        assert version is not None
        version.reviewed_at = datetime(2026, 7, 24, 15, 30, tzinfo=timezone.utc)
        with pytest.raises(BusinessError) as exc_info:
            adapter.record_oa_notice_from_evidence(_command(), transaction)
    assert exc_info.value.status_code == 409
    _assert_no_activity(session_factory)


@pytest.mark.parametrize("relationship", ("other_document", "other_case"))
def test_cross_document_or_case_evidence_is_400(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    relationship: str,
) -> None:
    _seed_valid(session_factory)
    _add_other_evidence(session_factory, other_case=relationship == "other_case")
    response = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID),
    )
    assert response.status_code == 400
    _assert_no_write(session_factory)


def test_missing_document_template_and_evidence_are_404(
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
    with session_factory() as transaction:
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        document.doc_template_id = None
        transaction.commit()
    missing_template = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    assert (
        missing_document.status_code,
        missing_template.status_code,
        missing_evidence.status_code,
    ) == (404, 404, 404)
    _assert_no_write(session_factory)


def test_api_uses_authenticated_actor_commits_once_and_returns_exact_result(
    session_factory: sessionmaker,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_valid(session_factory)
    actor_id = _actor_id(session_factory)
    adapter = _adapter()
    captured: list[object] = []
    result = adapter.RecordOaNoticeResult(
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        evidence_version_id=EVIDENCE_VERSION_ID,
        activity_id="activity-oa-notice-api",
        activity_sequence=1,
        lifecycle_revision=1,
        effective_at=EFFECTIVE_AT,
        occurred_at=None,
        official_due_date=OFFICIAL_DUE_DATE,
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
        oa_sequence=1,
        idempotency_key="oa-notice-1",
        reused=False,
    )

    def service(command: object, _transaction: object) -> object:
        captured.append(command)
        return result

    monkeypatch.setattr(documents_api, "record_oa_notice_from_evidence", service)
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
    assert response.json()["official_due_date"] == "2026-10-24"
    assert captured == [
        adapter.RecordOaNoticeCommand(
            document_id=DOCUMENT_ID,
            evidence_version_id=EVIDENCE_VERSION_ID,
            actor_id=actor_id,
            effective_at=EFFECTIVE_AT,
            occurred_at=None,
            idempotency_key="oa-notice-1",
        )
    ]
    assert recording.commit_calls == 1
    assert recording.rollback_calls == 0
    assert recording.close_calls == 0


def test_fresh_and_identical_replay_persist_one_exact_activity(
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
        assert case.status == "OA1"
        assert case.official_procedure_stage == OfficialProcedureStage.OFFICE_ACTION_RESPONSE.value
        assert case.lifecycle_revision == 1
        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == CASE_ID)
        ).all()
        references = transaction.scalars(select(CaseActivityEventEvidence)).all()
        assert len(activities) == len(references) == 1
        assert json.loads(activities[0].payload_json) == {
            "official_due_date": "2026-10-24",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
            "oa_sequence": 1,
            "source_template_code": "OA_IN",
        }
        assert (
            references[0].evidence_kind,
            references[0].object_type,
            references[0].object_id,
            references[0].content_hash,
            references[0].captured_at,
        ) == (
            "OA_NOTICE",
            "DocumentEvidenceVersion",
            EVIDENCE_VERSION_ID,
            CONTENT_HASH,
            REVIEWED_AT,
        )


def test_same_sequence_different_source_template_is_409_without_second_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    _seed_valid(session_factory, template_code="OA_IN")
    fresh = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    with session_factory() as transaction:
        replacement = _template(
            template_id="template-oa-notice-same-sequence",
            code="OFFICIAL_NOTICE_003",
        )
        transaction.add(replacement)
        document = transaction.get(Document, DOCUMENT_ID)
        assert document is not None
        document.doc_template_id = replacement.id
        transaction.commit()

    replay = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )

    assert fresh.status_code == 200
    assert replay.status_code == 409
    with session_factory() as transaction:
        case = transaction.get(Case, CASE_ID)
        assert case is not None and case.lifecycle_revision == 1
        assert transaction.scalar(select(func.count()).select_from(CaseActivityEvent)) == 1
        assert (
            transaction.scalar(select(func.count()).select_from(CaseActivityEventEvidence))
            == 1
        )


@pytest.mark.parametrize(
    "changed",
    (
        "document",
        "evidence",
        "hash",
        "reviewed_at",
        "due_date",
        "source",
        "sequence",
        "effective_at",
        "occurred_at",
    ),
)
def test_same_key_changed_bound_fact_is_409_without_second_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    changed: str,
) -> None:
    _seed_valid(session_factory)
    if changed == "document":
        _add_other_evidence(session_factory)
    elif changed == "evidence":
        _add_other_evidence(session_factory, same_document=True)
    first = client.post(
        PATH.format(document_id=DOCUMENT_ID),
        headers=auth_headers,
        json=_request_data(),
    )
    target_document = DOCUMENT_ID
    payload = _request_data()
    if changed == "document":
        target_document = OTHER_DOCUMENT_ID
        payload = _request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID)
    elif changed == "evidence":
        payload = _request_data(evidence_version_id=OTHER_EVIDENCE_VERSION_ID)
    elif changed in {"hash", "reviewed_at"}:
        with session_factory() as transaction:
            version = transaction.get(DocumentEvidenceVersion, EVIDENCE_VERSION_ID)
            assert version is not None
            if changed == "hash":
                version.content_hash = f"sha256:{'d' * 64}"
            else:
                version.reviewed_at = datetime(2026, 7, 24, 15, 31)
            transaction.commit()
    elif changed in {"due_date", "source"}:
        with session_factory() as transaction:
            document = transaction.get(Document, DOCUMENT_ID)
            assert document is not None
            document.extra_data = (
                _deadline_extra_data(due_date="2026-10-25")
                if changed == "due_date"
                else _deadline_extra_data(source="IMPORTED_OFFICIAL_NOTICE")
            )
            transaction.commit()
    elif changed == "sequence":
        with session_factory() as transaction:
            replacement = _template(
                template_id="template-oa-notice-second",
                code="OFFICIAL_NOTICE_005",
            )
            transaction.add(replacement)
            document = transaction.get(Document, DOCUMENT_ID)
            assert document is not None
            document.doc_template_id = replacement.id
            transaction.commit()
    elif changed == "effective_at":
        payload = _request_data(effective_at="2026-07-24T16:01:00")
    elif changed == "occurred_at":
        payload = _request_data(occurred_at="2026-07-24T15:55:00")
    drift = client.post(
        PATH.format(document_id=target_document),
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
    first = _command(actor_id="actor-oa-one", occurred_at=None)
    with session_factory() as transaction:
        adapter.record_oa_notice_from_evidence(first, transaction)
        transaction.commit()
    with session_factory() as transaction, pytest.raises(BusinessError) as exc_info:
        adapter.record_oa_notice_from_evidence(
            replace(first, actor_id="actor-oa-two"),
            transaction,
        )
    assert exc_info.value.status_code == 409
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
    user_id = "oa-notice-no-permission"
    with session_factory() as transaction:
        transaction.add(
            T_User(
                id=user_id,
                username=user_id,
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
        case.status = "OA1"
        document.title = "mutated"
        version.content_hash = f"sha256:{'d' * 64}"
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
        assert document is not None and document.title == "审查意见通知书"
        assert version is not None and version.content_hash == CONTENT_HASH
    _assert_no_write(session_factory)
