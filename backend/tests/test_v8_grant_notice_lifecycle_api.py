from __future__ import annotations

import inspect
import json
from datetime import date, datetime
from types import SimpleNamespace
from typing import get_type_hints
from uuid import uuid4

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    LegalStatus,
    LifecycleProjection,
    LifecycleTransitionResult,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.fees.models import T_GrantFeeTask
from app.modules.grant_fees import api as grant_fees_api

ROUTER_PATH = "/grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice"
API_PATH = "/api/v1/grant-fee-tasks/{task_id}/lifecycle/grant-notice"
RECORDED_AT = datetime(2026, 8, 9, 18, 0)
CONTENT_HASH = f"sha256:{'a' * 64}"


def _route() -> APIRoute:
    matches = [
        route
        for route in grant_fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _payload_type() -> type[BaseModel]:
    payload_type = get_type_hints(_route().endpoint)["payload"]
    assert isinstance(payload_type, type)
    assert issubclass(payload_type, BaseModel)
    return payload_type


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _request_data(**overrides: object) -> dict[str, object]:
    return {
        "reviewed_evidence_version_id": "evidence-1",
        "expected_content_hash": CONTENT_HASH,
        "recorded_at": "2026-08-09T18:00:00",
        "idempotency_key": "grant-api-1",
        **overrides,
    }


def _transition_result(*, reused: bool = False) -> LifecycleTransitionResult:
    previous = LifecycleProjection(
        business_stage=BusinessStage.PROSECUTION_MANAGEMENT,
        official_procedure_stage=OfficialProcedureStage.SUBSTANTIVE_EXAMINATION,
        legal_status=LegalStatus.APPLICATION_PENDING,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    )
    current = LifecycleProjection(
        business_stage=BusinessStage.GRANT_REGISTRATION_IN_PROGRESS,
        official_procedure_stage=OfficialProcedureStage.GRANT_REGISTRATION,
        legal_status=LegalStatus.APPLICATION_PENDING,
        lifecycle_verification_status=ConfirmationStatus.CONFIRMED,
    )
    return LifecycleTransitionResult(
        case_id="case-1",
        activity_id="activity-1",
        sequence=1,
        lifecycle_revision=1,
        lane=ActivityLane.LIFECYCLE,
        event_type="GRANT_REGISTRATION_NOTICE_RECORDED",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        previous_projection=previous,
        current_projection=current,
        legacy_case_status="GRANT_PENDING",
        idempotency_key="grant-registration-notice:grant-api-1",
        reused=reused,
    )


class RecordingSession:
    def __init__(
        self,
        source_document_id: object = "document-1",
        *,
        commit_error: Exception | None = None,
    ) -> None:
        self.task = SimpleNamespace(id="task-1", source_document_id=source_document_id)
        self.commit_error = commit_error
        self.commit_calls = 0
        self.rollback_calls = 0

    def get(self, model: object, identity: str) -> object | None:
        if model is T_GrantFeeTask and identity == "task-1":
            return self.task
        return None

    def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollback_calls += 1


def test_route_and_strict_body_are_exact() -> None:
    route = _route()
    assert route.status_code == 200
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Doc.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    assert next(item.call for item in route.dependant.dependencies if item.name == "db") is get_db
    payload_type = _payload_type()
    assert tuple(payload_type.model_fields) == (
        "reviewed_evidence_version_id",
        "expected_content_hash",
        "recorded_at",
        "idempotency_key",
    )
    assert payload_type.model_config["extra"] == "forbid"
    parsed = payload_type.model_validate(_request_data())
    assert parsed.recorded_at == RECORDED_AT
    with pytest.raises(ValidationError):
        payload_type.model_validate({**_request_data(), "case_id": "client-owned"})


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("reviewed_evidence_version_id", " evidence"),
        ("reviewed_evidence_version_id", "x" * 37),
        ("expected_content_hash", "a" * 64),
        ("expected_content_hash", f"sha256:{'A' * 64}"),
        ("expected_content_hash", f"xsha256:{'a' * 64}"),
        ("recorded_at", "2026-08-09T18:00:00Z"),
        ("idempotency_key", " key"),
        ("idempotency_key", "x" * 103),
    ),
)
def test_body_shape_failures_are_422(field: str, value: object) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: RecordingSession()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(
            API_PATH.format(task_id="task-1"), json=_request_data(**{field: value})
        )
    assert response.status_code == 422


@pytest.mark.parametrize("task_id", (" task", "task ", "x" * 37))
def test_path_shape_failures_are_422(task_id: str) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: RecordingSession()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(API_PATH.format(task_id=task_id), json=_request_data())
    assert response.status_code == 422


def test_server_actor_exact_delegation_and_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    session = RecordingSession()
    calls: list[dict[str, object]] = []

    def dispatch(**kwargs: object) -> LifecycleTransitionResult:
        calls.append(kwargs)
        return _transition_result()

    monkeypatch.setattr(grant_fees_api, "dispatch_grant_registration_notice", dispatch)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(API_PATH.format(task_id="task-1"), json=_request_data())

    assert response.status_code == 200, response.text
    assert response.json()["event_type"] == "GRANT_REGISTRATION_NOTICE_RECORDED"
    assert calls == [
        {
            "grant_fee_task_id": "task-1",
            "source_document_id": "document-1",
            "reviewed_evidence_version_id": "evidence-1",
            "expected_content_hash": CONTENT_HASH,
            "actor_id": "actor-1",
            "recorded_at": RECORDED_AT,
            "idempotency_key": "grant-api-1",
            "transaction": session,
        }
    ]
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


@pytest.mark.parametrize("source_document_id", (None, "", " document", "x" * 37))
def test_invalid_stored_source_is_write_free_409(source_document_id: object) -> None:
    session = RecordingSession(source_document_id)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(API_PATH.format(task_id="task-1"), json=_request_data())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "GRANT_NOTICE_LIFECYCLE_SOURCE_CONFLICT"
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_missing_task_is_404_and_service_failure_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = RecordingSession()
    missing.task = None
    app = create_app()
    app.dependency_overrides[get_db] = lambda: missing
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(API_PATH.format(task_id="task-1"), json=_request_data())
    assert response.status_code == 404
    assert missing.rollback_calls == 1


def test_service_failure_rolls_back_and_preserves_business_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = RecordingSession()
    error = BusinessError(
        "GRANT_NOTICE_EVIDENCE_CONFLICT",
        "conflict",
        status_code=409,
    )

    def dispatch(**_kwargs: object) -> None:
        raise error

    monkeypatch.setattr(grant_fees_api, "dispatch_grant_registration_notice", dispatch)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id="actor-1")
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        response = client.post(API_PATH.format(task_id="task-1"), json=_request_data())

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "GRANT_NOTICE_EVIDENCE_CONFLICT"
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_commit_failure_rolls_back_and_reraises_original_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = RuntimeError("commit failed")
    session = RecordingSession(commit_error=error)
    monkeypatch.setattr(
        grant_fees_api,
        "dispatch_grant_registration_notice",
        lambda **_kwargs: _transition_result(),
    )

    with pytest.raises(RuntimeError) as exc_info:
        grant_fees_api.post_grant_notice_lifecycle_endpoint(
            grant_fee_task_id="task-1",
            payload=_payload_type().model_validate(_request_data()),
            _perm=None,
            current_user=SimpleNamespace(id="actor-1"),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


def _seed_real(session_factory: sessionmaker) -> tuple[str, str]:
    with session_factory() as db:
        template = db.query(DocTemplate).filter(DocTemplate.code == "GRANT_NOTICE").one()
        case = Case(
            id=str(uuid4()),
            case_no=f"V8-GRANT-API-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            status="SUB_EXAM",
            business_stage="PROSECUTION_MANAGEMENT",
            official_procedure_stage="SUBSTANTIVE_EXAMINATION",
            legal_status="APPLICATION_PENDING",
            lifecycle_verification_status="CONFIRMED",
            lifecycle_revision=0,
            app_no="CN2026000001",
            filing_date=date(2026, 1, 2),
            pub_no="CN123456789A",
            pub_date=date(2026, 6, 1),
            grant_no="CN123456789B",
            grant_date=date(2026, 7, 1),
            first_annuity_year=1,
            valid_until=date(2046, 1, 2),
        )
        document = Document(
            id=str(uuid4()),
            case_id=case.id,
            doc_template_id=template.id,
            doc_type="OFFICIAL_IN",
            direction="IN",
            doc_date=date(2026, 8, 9),
            title="办理登记手续通知书",
            extra_data=json.dumps(
                {
                    "GrantFeeLines": [
                        {
                            "fee_name": "授权当年年费",
                            "year": 1,
                            "amount": "900.00",
                            "reduction_ratio": "0.85",
                        }
                    ]
                },
                ensure_ascii=False,
            ),
        )
        task = T_GrantFeeTask(
            id=str(uuid4()),
            case_id=case.id,
            type="GRANT",
            due_date=date(2026, 10, 9),
            source_document_id=document.id,
            deadline_source="MANUAL_OFFICIAL_NOTICE",
            deadline_confirmed_at=datetime(2026, 8, 9, 17, 0),
            currency="CNY",
        )
        attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document.id,
            file_name="grant.pdf",
            file_path=f"attachments/{document.id}/grant.pdf",
            content_hash=CONTENT_HASH,
        )
        lineage = f"attachment:{attachment.id}"
        evidence = DocumentEvidenceVersion(
            id=str(uuid4()),
            case_id=case.id,
            document_id=document.id,
            attachment_id=attachment.id,
            lineage_key=lineage,
            role="OFFICIAL_FINAL_PDF",
            version_number=1,
            state="FINAL",
            creator_id=str(uuid4()),
            review_state="APPROVED",
            reviewer_id=str(uuid4()),
            reviewed_at=datetime(2026, 8, 9, 17, 30),
            content_hash=CONTENT_HASH,
            current_identity_key=f"{case.id}|{lineage}",
        )
        db.add(case)
        db.flush()
        db.add(document)
        db.flush()
        db.add_all((task, attachment))
        db.flush()
        db.add(evidence)
        db.commit()
        return task.id, evidence.id


def test_real_route_dispatch_and_exact_replay(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    task_id, evidence_id = _seed_real(session_factory)
    payload = _request_data(reviewed_evidence_version_id=evidence_id)
    first = client.post(API_PATH.format(task_id=task_id), headers=auth_headers, json=payload)
    replay = client.post(API_PATH.format(task_id=task_id), headers=auth_headers, json=payload)
    assert first.status_code == replay.status_code == 200
    assert first.json()["reused"] is False
    assert replay.json()["reused"] is True
    assert replay.json()["activity_id"] == first.json()["activity_id"]
