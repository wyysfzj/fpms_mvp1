from __future__ import annotations

import importlib
import importlib.util
import inspect
from datetime import date
from types import ModuleType, SimpleNamespace
from typing import Any, get_type_hints

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import get_current_user
from app.core.errors import BusinessError
from app.db.session import get_db
from app.main import create_app
from app.modules.fees import api as fees_api
from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
    FeeDomain,
    FeeEstimateStatus,
    FeeObligation,
    FeeObligationDraftStatus,
    FeeObligationSource,
    FeeObligationStatus,
    FeeObligationStatuses,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentStatus,
    FeeSourceStatus,
    RecordFeeObligationInstructionCommand,
    RecordFeeObligationInstructionResult,
)

PATH = "/api/v1/fees/obligations/obligation-1/instruction"
ROUTER_PATH = "/fees/obligations/{obligation_id}/instruction"
ACTOR_ID = "actor-1"

INPUT_FIELDS = ("instruction", "idempotency_key")
OUTPUT_FIELDS = (
    "obligation_id",
    "client_instruction_status",
    "activity_id",
    "idempotency_key",
    "reused",
)


class RecordingSession:
    def __init__(self, *, commit_error: Exception | None = None) -> None:
        self.commit_error = commit_error
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollback_calls += 1

    def _forbidden(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("instruction adapter performed an extra database operation")

    add = add_all = delete = execute = flush = get = query = refresh = _forbidden


def _schemas() -> ModuleType:
    module_name = "app.modules.fees.obligation_schemas"
    assert importlib.util.find_spec(module_name) is not None, (
        "missing frozen fee-obligation instruction schemas"
    )
    return importlib.import_module(module_name)


def _route() -> APIRoute:
    matching = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute) and route.path == ROUTER_PATH
    ]
    assert len(matching) == 1
    return matching[0]


def _permission_dependency() -> object:
    dependency = next(item for item in _route().dependant.dependencies if item.name == "_perm")
    return dependency.call


def _request_data(
    *,
    instruction: str = "PAY",
    idempotency_key: str = "idem-1",
) -> dict[str, object]:
    return {
        "instruction": instruction,
        "idempotency_key": idempotency_key,
    }


def _result(
    *,
    instruction_status: FeeClientInstructionStatus = FeeClientInstructionStatus.PAY,
    activity_id: str = "activity-1",
    idempotency_key: str = "idem-1",
    reused: bool = False,
) -> RecordFeeObligationInstructionResult:
    return RecordFeeObligationInstructionResult(
        obligation=FeeObligation(
            id="obligation-1",
            case_id="case-1",
            source=FeeObligationSource(
                source_activity_id="recognition-activity-1",
                source_document_id="document-1",
                status=FeeSourceStatus.VERIFIED,
            ),
            fee_domain=FeeDomain.GOV,
            obligation_type="APPLICATION_FEE",
            due_date=date(2026, 8, 15),
            currency="CNY",
            statuses=FeeObligationStatuses(
                estimate_status=FeeEstimateStatus.ESTIMATE,
                obligation_status=FeeObligationStatus.RECOGNIZED,
                client_instruction_status=instruction_status,
                draft_status=FeeObligationDraftStatus.NOT_CREATED,
                pay_list_status=FeePayListStatus.NOT_CREATED,
                payment_status=FeePaymentStatus.UNPAID,
                official_evidence_status=FeeOfficialEvidenceStatus.PENDING,
            ),
            lines=(),
            supersedes_obligation_id=None,
            supersede_reason=None,
        ),
        activity_id=activity_id,
        idempotency_key=idempotency_key,
        reused=reused,
    )


def _client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    service_result: RecordFeeObligationInstructionResult | None = None,
    service_error: BusinessError | None = None,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession, list[RecordFeeObligationInstructionCommand]]:
    session = RecordingSession()
    actor = SimpleNamespace(id=ACTOR_ID)
    captured: list[RecordFeeObligationInstructionCommand] = []

    def service(
        command: RecordFeeObligationInstructionCommand,
        transaction: object,
    ) -> RecordFeeObligationInstructionResult:
        assert transaction is session
        captured.append(command)
        if service_error is not None:
            raise service_error
        assert service_result is not None
        return service_result

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(fees_api, "record_client_instruction", service, raising=False)
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: actor
    app.dependency_overrides[_permission_dependency()] = permission
    return TestClient(app), session, captured


def test_frozen_schemas_have_exact_order_annotations_enum_and_strict_input() -> None:
    schemas = _schemas()
    input_schema = schemas.FeeObligationInstructionIn
    output_schema = schemas.FeeObligationInstructionOut

    assert tuple(input_schema.model_fields) == INPUT_FIELDS
    assert get_type_hints(input_schema) == {
        "instruction": FeeClientInstruction,
        "idempotency_key": str,
    }
    assert input_schema.model_config["extra"] == "forbid"
    assert all(field.is_required() for field in input_schema.model_fields.values())
    assert tuple(member.value for member in FeeClientInstruction) == ("PAY", "HOLD", "ABANDON")

    assert tuple(output_schema.model_fields) == OUTPUT_FIELDS
    assert get_type_hints(output_schema) == {
        "obligation_id": str,
        "client_instruction_status": FeeClientInstructionStatus,
        "activity_id": str,
        "idempotency_key": str,
        "reused": bool,
    }

    for forbidden in ("obligation_id", "actor_id", "unexpected"):
        with pytest.raises(ValidationError):
            input_schema.model_validate({**_request_data(), forbidden: "client-owned"})


def test_route_is_one_post_with_fee_edit_permission_server_actor_and_direct_model() -> None:
    route = _route()
    schemas = _schemas()

    assert route.methods == {"POST"}
    assert route.status_code == 200
    assert route.response_model is schemas.FeeObligationInstructionOut
    assert inspect.getclosurevars(_permission_dependency()).nonlocals["code"] == "Fee.Edit"
    assert (
        next(item.call for item in route.dependant.dependencies if item.name == "current_user")
        is get_current_user
    )
    signature = inspect.signature(fees_api.record_fee_obligation_instruction)
    assert list(signature.parameters) == [
        "obligation_id",
        "payload",
        "_perm",
        "current_user",
        "db",
    ]

    instruction_routes = [
        item
        for item in fees_api.router.routes
        if isinstance(item, APIRoute)
        and item.path.startswith("/fees/obligations")
        and "instruction" in item.path
    ]
    assert instruction_routes == [route]


@pytest.mark.parametrize(
    ("instruction", "instruction_status"),
    [
        (FeeClientInstruction.PAY, FeeClientInstructionStatus.PAY),
        (FeeClientInstruction.HOLD, FeeClientInstructionStatus.HOLD),
        (FeeClientInstruction.ABANDON, FeeClientInstructionStatus.ABANDON),
    ],
)
def test_handler_projects_one_exact_server_owned_command_and_only_commits(
    monkeypatch: pytest.MonkeyPatch,
    instruction: FeeClientInstruction,
    instruction_status: FeeClientInstructionStatus,
) -> None:
    schemas = _schemas()
    session = RecordingSession()
    result = _result(instruction_status=instruction_status)
    captured: list[RecordFeeObligationInstructionCommand] = []

    def service(
        command: RecordFeeObligationInstructionCommand,
        transaction: object,
    ) -> RecordFeeObligationInstructionResult:
        assert transaction is session
        captured.append(command)
        return result

    monkeypatch.setattr(fees_api, "record_client_instruction", service, raising=False)
    actual = fees_api.record_fee_obligation_instruction(
        obligation_id="obligation-1",
        payload=schemas.FeeObligationInstructionIn(
            instruction=instruction,
            idempotency_key="idem-1",
        ),
        _perm=None,
        current_user=SimpleNamespace(id=ACTOR_ID),
        db=session,
    )

    assert captured == [
        RecordFeeObligationInstructionCommand(
            obligation_id="obligation-1",
            instruction=instruction,
            actor_id=ACTOR_ID,
            idempotency_key="idem-1",
        )
    ]
    assert actual == schemas.FeeObligationInstructionOut(
        obligation_id="obligation-1",
        client_instruction_status=instruction_status,
        activity_id="activity-1",
        idempotency_key="idem-1",
        reused=False,
    )
    assert session.commit_calls == 1
    assert session.rollback_calls == 0

    source = inspect.getsource(fees_api.record_fee_obligation_instruction)
    assert source.count("record_client_instruction(") == 1
    for forbidden in (
        "FeeDraft",
        "PayList",
        "payment",
        "lifecycle",
        ".refresh(",
        ".execute(",
        "retry",
    ):
        assert forbidden not in source


@pytest.mark.parametrize(
    ("service_result", "expected"),
    [
        (
            _result(),
            {
                "obligation_id": "obligation-1",
                "client_instruction_status": "PAY",
                "activity_id": "activity-1",
                "idempotency_key": "idem-1",
                "reused": False,
            },
        ),
        (
            _result(
                instruction_status=FeeClientInstructionStatus.HOLD,
                activity_id="original-activity",
                idempotency_key="original-key",
                reused=True,
            ),
            {
                "obligation_id": "obligation-1",
                "client_instruction_status": "HOLD",
                "activity_id": "original-activity",
                "idempotency_key": "original-key",
                "reused": True,
            },
        ),
    ],
)
def test_new_and_replayed_results_return_direct_five_field_200_and_commit_once(
    monkeypatch: pytest.MonkeyPatch,
    service_result: RecordFeeObligationInstructionResult,
    expected: dict[str, object],
) -> None:
    client, session, captured = _client(monkeypatch, service_result=service_result)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == 200
    assert response.json() == expected
    assert "data" not in response.json()
    assert len(captured) == 1
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_service_business_error_rolls_back_once_and_is_reraised_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schemas = _schemas()
    error = BusinessError(
        "FEE_OBLIGATION_INSTRUCTION_CONFLICT",
        "conflict",
        details={"marker": "service"},
        status_code=409,
    )
    session = RecordingSession()

    def service(*_args: object, **_kwargs: object) -> None:
        raise error

    monkeypatch.setattr(fees_api, "record_client_instruction", service, raising=False)
    with pytest.raises(BusinessError) as exc_info:
        fees_api.record_fee_obligation_instruction(
            obligation_id="obligation-1",
            payload=schemas.FeeObligationInstructionIn.model_validate(_request_data()),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_commit_failure_rolls_back_once_and_reraises_original_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schemas = _schemas()
    error = RuntimeError("commit failed")
    session = RecordingSession(commit_error=error)
    monkeypatch.setattr(
        fees_api,
        "record_client_instruction",
        lambda *_args: _result(),
        raising=False,
    )

    with pytest.raises(RuntimeError) as exc_info:
        fees_api.record_fee_obligation_instruction(
            obligation_id="obligation-1",
            payload=schemas.FeeObligationInstructionIn.model_validate(_request_data()),
            _perm=None,
            current_user=SimpleNamespace(id=ACTOR_ID),
            db=session,
        )

    assert exc_info.value is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1


@pytest.mark.parametrize(
    ("status_code", "code"),
    [
        (400, "FEE_CLIENT_INSTRUCTION_COMMAND_INVALID"),
        (404, "FEE_OBLIGATION_NOT_FOUND"),
        (404, "CASE_NOT_FOUND"),
        (409, "FEE_CLIENT_INSTRUCTION_RECOGNITION_INVALID"),
        (409, "FEE_CLIENT_INSTRUCTION_STORED_STATE_INVALID"),
        (409, "FEE_CLIENT_INSTRUCTION_LOCKED"),
        (409, "FEE_CLIENT_INSTRUCTION_SAME_STATE"),
        (409, "FEE_CLIENT_INSTRUCTION_IDEMPOTENCY_CONFLICT"),
        (409, "FEE_CLIENT_INSTRUCTION_CONCURRENCY_CONFLICT"),
    ],
)
def test_service_business_error_matrix_passes_through_http_unchanged(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
    code: str,
) -> None:
    error = BusinessError(
        code,
        "service error",
        details={"marker": code},
        status_code=status_code,
    )
    client, session, captured = _client(monkeypatch, service_error=error)

    response = client.post(PATH, json=_request_data())

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": "service error",
            "details": {"marker": code},
        }
    }
    assert len(captured) == 1
    assert session.commit_calls == 0
    assert session.rollback_calls == 1


def test_authentication_and_permission_dependencies_preserve_401_and_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: RecordingSession()
    app.dependency_overrides[_permission_dependency()] = lambda: None
    with TestClient(app) as client:
        missing = client.post(PATH, json=_request_data())
        invalid = client.post(
            PATH,
            json=_request_data(),
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTH_REQUIRED"
    assert invalid.status_code == 401
    assert invalid.json()["error"]["code"] == "AUTH_REQUIRED"

    forbidden = BusinessError(
        "FORBIDDEN",
        "Permission denied",
        details={"required_perm": "Fee.Edit"},
        status_code=403,
    )
    client, session, captured = _client(
        monkeypatch,
        service_result=_result(),
        permission_error=forbidden,
    )
    response = client.post(PATH, json=_request_data())

    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "code": "FORBIDDEN",
            "message": "Permission denied",
            "details": {"required_perm": "Fee.Edit"},
        }
    }
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


@pytest.mark.parametrize(
    "invalid",
    [
        {},
        {"instruction": "PAY"},
        {"idempotency_key": "idem-1"},
        {**_request_data(), "instruction": "UNKNOWN"},
        {**_request_data(), "obligation_id": "client-obligation"},
        {**_request_data(), "actor_id": "client-actor"},
        {**_request_data(), "unexpected": True},
    ],
)
def test_invalid_or_legacy_request_shape_returns_422_without_service_or_transaction(
    monkeypatch: pytest.MonkeyPatch,
    invalid: dict[str, Any],
) -> None:
    client, session, captured = _client(monkeypatch, service_result=_result())

    response = client.post(PATH, json=invalid)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


def test_collection_action_and_legacy_body_id_routes_do_not_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session, captured = _client(monkeypatch, service_result=_result())

    collection = client.post("/api/v1/fees/obligations/instruction", json=_request_data())
    legacy = client.post(
        "/api/v1/fees/obligations",
        json={**_request_data(), "obligation_id": "obligation-1"},
    )

    collection_post_routes = [
        route
        for route in fees_api.router.routes
        if isinstance(route, APIRoute)
        and route.path == "/fees/obligations/instruction"
        and "POST" in route.methods
    ]
    assert collection_post_routes == []
    assert collection.status_code == 405
    assert collection.headers["allow"] == "GET"
    assert legacy.status_code == 404
    assert captured == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0
