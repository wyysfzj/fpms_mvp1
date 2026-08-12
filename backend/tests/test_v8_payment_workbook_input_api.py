from __future__ import annotations

import inspect
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
from threading import Event, Thread
from types import SimpleNamespace

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.errors import BusinessError, raise_business_error
from app.db.session import get_db
from app.main import create_app
from app.modules.annuity import api as annuity_api
from app.modules.annuity.official_payment_workbook_input_schemas import (
    ActivateWorkbookInputIn,
    RetireWorkbookInputIn,
    ReviewWorkbookInputIn,
    WorkbookInputOut,
)
from app.modules.annuity.official_payment_workbook_input_service import (
    ActivateWorkbookInputCommand,
    RegisterWorkbookInputCommand,
    RetireWorkbookInputCommand,
    ReviewWorkbookInputCommand,
    ValidateWorkbookInputCommand,
    WorkbookInputResult,
)

NOW = datetime(2026, 8, 13, 12, 0)
LATER = NOW + timedelta(days=365)
ACTOR_ID = "00000000-0000-4000-8000-000000000001"
VERSION_ID = "11111111-1111-4111-8111-111111111111"
FIXTURE = Path(__file__).parent / "fixtures" / "v8_verified_official_payment_template.xlsm"


class RecordingSession:
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1


def _result(disposition: str = "UPDATED") -> WorkbookInputResult:
    return WorkbookInputResult(
        version_id=VERSION_ID,
        scope_key="GLOBAL",
        source_classification="PRODUCTION",
        template_version="2026.08",
        template_storage_path="/secret/managed/template.xlsm",
        template_content_hash="a" * 64,
        upload_proof_storage_path="/secret/managed/upload-proof.bin",
        upload_proof_content_hash="b" * 64,
        structure_snapshot_hash="c" * 64,
        workflow_status="APPROVED",
        activation_status="INACTIVE",
        effective_from=NOW,
        effective_to=LATER,
        supersedes_version_id=None,
        current_identity_key=None,
        created_by=ACTOR_ID,
        validated_by=ACTOR_ID,
        validated_at=NOW,
        reviewed_by="00000000-0000-4000-8000-000000000002",
        reviewed_at=NOW,
        activated_by=None,
        activated_at=None,
        retired_by=None,
        retired_at=None,
        retirement_reason=None,
        disposition=disposition,
    )


def _route(path: str) -> APIRoute:
    matches = [
        route
        for route in annuity_api.router.routes
        if isinstance(route, APIRoute) and route.path == path and route.methods == {"POST"}
    ]
    assert len(matches) == 1
    return matches[0]


def _permission_dependency(path: str) -> object:
    return next(item.call for item in _route(path).dependant.dependencies if item.name == "_perm")


def _client(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    permission_error: BusinessError | None = None,
) -> tuple[TestClient, RecordingSession]:
    transaction = RecordingSession()

    def permission() -> None:
        if permission_error is not None:
            raise permission_error

    monkeypatch.setattr(annuity_api, "_payment_workbook_storage_root", lambda: tmp_path)
    monkeypatch.setattr(annuity_api, "_utcnow", lambda: NOW)
    monkeypatch.setattr(
        annuity_api,
        "_runtime_profile",
        lambda: "production",
    )
    app = create_app()
    app.dependency_overrides[get_db] = lambda: transaction
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=ACTOR_ID)
    for path in (
        "/payment-workbook-inputs",
        "/payment-workbook-inputs/{version_id}/validate",
        "/payment-workbook-inputs/{version_id}/review",
        "/payment-workbook-inputs/{version_id}/activate",
        "/payment-workbook-inputs/{version_id}/retire",
    ):
        app.dependency_overrides[_permission_dependency(path)] = permission
    return TestClient(app), transaction


def _register_data(**overrides: str) -> dict[str, str]:
    data = {
        "template_version": "2026.08",
        "effective_from": NOW.isoformat(),
        "effective_to": LATER.isoformat(),
        "source_classification": "PRODUCTION",
        "idempotency_key": "register-workbook-v1",
    }
    data.update(overrides)
    return data


def _files(proof: bytes = b'{"controlled_upload":true}') -> dict[str, tuple[str, bytes, str]]:
    return {
        "template_file": (
            "untrusted-client-name.xlsm",
            FIXTURE.read_bytes(),
            "application/vnd.ms-excel.sheet.macroEnabled.12",
        ),
        "upload_proof_file": ("untrusted-proof.json", proof, "application/json"),
    }


def test_strict_schemas_and_routes_freeze_server_owned_fields() -> None:
    assert tuple(ReviewWorkbookInputIn.model_fields) == ("decision", "reason")
    assert tuple(ActivateWorkbookInputIn.model_fields) == ("idempotency_key",)
    assert tuple(RetireWorkbookInputIn.model_fields) == ("reason", "idempotency_key")
    assert "template_storage_path" not in WorkbookInputOut.model_fields
    assert "upload_proof_storage_path" not in WorkbookInputOut.model_fields
    assert "runtime_profile" not in WorkbookInputOut.model_fields
    for path in (
        "/payment-workbook-inputs",
        "/payment-workbook-inputs/{version_id}/validate",
        "/payment-workbook-inputs/{version_id}/review",
        "/payment-workbook-inputs/{version_id}/activate",
        "/payment-workbook-inputs/{version_id}/retire",
    ):
        dependency = _permission_dependency(path)
        assert inspect.getclosurevars(dependency).nonlocals["code"] == "Fee.Edit"


def test_register_stores_generated_paths_commits_and_returns_201_or_200_replay(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[RegisterWorkbookInputCommand] = []

    def register(transaction, command: RegisterWorkbookInputCommand) -> WorkbookInputResult:
        assert isinstance(transaction, RecordingSession)
        calls.append(command)
        template = Path(command.template_storage_path)
        proof = Path(command.upload_proof_storage_path)
        assert template.name == "template.xlsm"
        assert proof.name == "upload-proof.bin"
        assert "untrusted" not in str(template)
        assert template.is_file() and proof.is_file()
        assert command.expected_template_hash == sha256(template.read_bytes()).hexdigest()
        assert command.expected_upload_proof_hash == sha256(proof.read_bytes()).hexdigest()
        assert command.actor_id == ACTOR_ID
        assert command.runtime_profile == "production"
        return _result("CREATED" if len(calls) == 1 else "REUSED")

    monkeypatch.setattr(annuity_api, "register_workbook_input", register)
    client, transaction = _client(monkeypatch, tmp_path)
    first = client.post("/api/v1/payment-workbook-inputs", data=_register_data(), files=_files())
    assert first.status_code == 201
    assert first.json()["version_id"] == VERSION_ID
    assert "template_storage_path" not in first.json()
    second = client.post("/api/v1/payment-workbook-inputs", data=_register_data(), files=_files())
    assert second.status_code == 200
    assert calls[0].template_storage_path == calls[1].template_storage_path
    assert transaction.commit_calls == 2
    assert transaction.rollback_calls == 0


def test_register_failure_rolls_back_and_cleans_only_new_request_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def reject(_transaction, _command) -> WorkbookInputResult:
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "conflict",
            status_code=409,
        )

    monkeypatch.setattr(annuity_api, "register_workbook_input", reject)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(idempotency_key="cleanup-new-files"),
        files=_files(),
    )
    assert response.status_code == 409
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1
    assert list(tmp_path.rglob("*")) == []


def test_register_conflicting_or_partial_replay_fails_closed_without_service_call(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key = "conflicting-replay"
    directory = tmp_path / sha256(key.encode()).hexdigest()
    directory.mkdir()
    (directory / "template.xlsm").write_bytes(b"different")
    called = False

    def register(_transaction, _command) -> WorkbookInputResult:
        nonlocal called
        called = True
        return _result()

    monkeypatch.setattr(annuity_api, "register_workbook_input", register)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(idempotency_key=key),
        files=_files(),
    )
    assert response.status_code == 409
    assert called is False
    assert transaction.rollback_calls == 1
    assert (directory / "template.xlsm").read_bytes() == b"different"
    assert not (directory / "upload-proof.bin").exists()


def test_register_failure_never_removes_exact_replay_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key = "existing-replay"
    directory = tmp_path / sha256(key.encode()).hexdigest()
    directory.mkdir()
    template = directory / "template.xlsm"
    proof = directory / "upload-proof.bin"
    template.write_bytes(FIXTURE.read_bytes())
    proof.write_bytes(b'{"controlled_upload":true}')

    def reject(_transaction, _command) -> WorkbookInputResult:
        raise_business_error("PAYMENT_WORKBOOK_INPUT_CONFLICT", "conflict", status_code=409)

    monkeypatch.setattr(annuity_api, "register_workbook_input", reject)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(idempotency_key=key),
        files=_files(),
    )
    assert response.status_code == 409
    assert transaction.rollback_calls == 1
    assert template.read_bytes() == FIXTURE.read_bytes()
    assert proof.read_bytes() == b'{"controlled_upload":true}'


def test_register_serializes_publication_through_transaction_and_cleanup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    first_entered = Event()
    release_first = Event()
    second_entered = Event()
    responses: dict[str, object] = {}
    calls = 0

    def register(_transaction, _command) -> WorkbookInputResult:
        nonlocal calls
        calls += 1
        if calls == 1:
            first_entered.set()
            assert release_first.wait(5)
            raise_business_error(
                "PAYMENT_WORKBOOK_INPUT_CONFLICT",
                "owner failed",
                status_code=409,
            )
        second_entered.set()
        return _result("CREATED")

    monkeypatch.setattr(annuity_api, "register_workbook_input", register)
    client, transaction = _client(monkeypatch, tmp_path)

    def request(name: str) -> None:
        responses[name] = client.post(
            "/api/v1/payment-workbook-inputs",
            data=_register_data(idempotency_key="concurrent-publish"),
            files=_files(),
        )

    owner = Thread(target=request, args=("owner",))
    replay = Thread(target=request, args=("replay",))
    owner.start()
    assert first_entered.wait(5)
    replay.start()
    assert not second_entered.wait(0.2)
    release_first.set()
    owner.join(5)
    replay.join(5)
    assert not owner.is_alive() and not replay.is_alive()
    assert responses["owner"].status_code == 409
    assert responses["replay"].status_code == 201
    directory = tmp_path / sha256(b"concurrent-publish").hexdigest()
    assert (directory / "template.xlsm").is_file()
    assert (directory / "upload-proof.bin").is_file()
    assert transaction.rollback_calls == 1
    assert transaction.commit_calls == 1


def test_keyed_directory_symlink_is_409_without_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key = "symlink-replay"
    target = tmp_path / "other-directory"
    target.mkdir()
    directory = tmp_path / sha256(key.encode()).hexdigest()
    directory.symlink_to(target, target_is_directory=True)
    called = False

    def register(_transaction, _command) -> WorkbookInputResult:
        nonlocal called
        called = True
        return _result()

    monkeypatch.setattr(annuity_api, "register_workbook_input", register)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(idempotency_key=key),
        files=_files(),
    )
    assert response.status_code == 409
    assert called is False
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1
    assert list(target.iterdir()) == []


def test_managed_file_symlink_is_rejected_before_external_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside.bin"
    outside.write_bytes(b"must remain unchanged")
    original = annuity_api._save_upload_no_follow
    injected = False

    def inject_symlink(upload, directory, name, identity) -> None:
        nonlocal injected
        if not injected:
            injected = True
            (directory / name).symlink_to(outside)
        original(upload, directory, name, identity)

    monkeypatch.setattr(annuity_api, "_save_upload_no_follow", inject_symlink)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(idempotency_key="file-symlink"),
        files=_files(),
    )
    assert response.status_code == 409
    assert transaction.commit_calls == 0
    assert transaction.rollback_calls == 1
    assert outside.read_bytes() == b"must remain unchanged"


@pytest.mark.parametrize(
    ("path", "payload", "service_name", "command_type"),
    [
        (
            f"/api/v1/payment-workbook-inputs/{VERSION_ID}/validate",
            None,
            "validate_workbook_input",
            ValidateWorkbookInputCommand,
        ),
        (
            f"/api/v1/payment-workbook-inputs/{VERSION_ID}/review",
            {"decision": "APPROVE", "reason": "独立复核通过"},
            "review_workbook_input",
            ReviewWorkbookInputCommand,
        ),
        (
            f"/api/v1/payment-workbook-inputs/{VERSION_ID}/activate",
            {"idempotency_key": "register-workbook-v1"},
            "activate_workbook_input",
            ActivateWorkbookInputCommand,
        ),
        (
            f"/api/v1/payment-workbook-inputs/{VERSION_ID}/retire",
            {"reason": "机构管理员撤销", "idempotency_key": "register-workbook-v1"},
            "retire_workbook_input",
            RetireWorkbookInputCommand,
        ),
    ],
)
def test_transition_routes_use_server_actor_time_and_caller_transaction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    path: str,
    payload: dict[str, str] | None,
    service_name: str,
    command_type: type,
) -> None:
    seen: list[object] = []

    def service(transaction, command):
        assert isinstance(transaction, RecordingSession)
        seen.append(command)
        return _result()

    monkeypatch.setattr(annuity_api, service_name, service)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(path, json=payload) if payload is not None else client.post(path)
    assert response.status_code == 200
    assert isinstance(seen[0], command_type)
    assert seen[0].actor_id == ACTOR_ID
    if isinstance(seen[0], (ActivateWorkbookInputCommand, RetireWorkbookInputCommand)):
        assert seen[0].at == NOW
    if isinstance(seen[0], ActivateWorkbookInputCommand):
        assert seen[0].runtime_profile == "production"
    assert transaction.commit_calls == 1
    assert transaction.rollback_calls == 0


def test_test_only_production_registration_is_409_and_no_files_remain(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def reject(_transaction, command: RegisterWorkbookInputCommand) -> WorkbookInputResult:
        assert command.source_classification == "TEST_ONLY"
        assert command.runtime_profile == "production"
        raise_business_error(
            "PAYMENT_WORKBOOK_INPUT_CONFLICT",
            "TEST_ONLY cannot enter production",
            status_code=409,
        )

    monkeypatch.setattr(annuity_api, "register_workbook_input", reject)
    client, transaction = _client(monkeypatch, tmp_path)
    response = client.post(
        "/api/v1/payment-workbook-inputs",
        data=_register_data(source_classification="TEST_ONLY", idempotency_key="test-only-prod"),
        files=_files(),
    )
    assert response.status_code == 409
    assert transaction.rollback_calls == 1
    assert list(tmp_path.rglob("*")) == []


def test_auth_permission_and_payload_validation_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    anonymous = TestClient(create_app()).post(
        f"/api/v1/payment-workbook-inputs/{VERSION_ID}/review",
        json={"decision": "APPROVE", "reason": "review"},
    )
    assert anonymous.status_code == 401

    forbidden = BusinessError(
        "FORBIDDEN",
        "Forbidden",
        details={"required_perm": "Fee.Edit"},
        status_code=403,
    )
    client, transaction = _client(monkeypatch, tmp_path, permission_error=forbidden)
    denied = client.post(
        f"/api/v1/payment-workbook-inputs/{VERSION_ID}/review",
        json={"decision": "APPROVE", "reason": "review"},
    )
    assert denied.status_code == 403
    assert transaction.commit_calls == transaction.rollback_calls == 0
    invalid = client.post(
        f"/api/v1/payment-workbook-inputs/{VERSION_ID}/activate",
        json={"idempotency_key": "key", "runtime_profile": "production"},
    )
    assert invalid.status_code == 403

    allowed, allowed_transaction = _client(monkeypatch, tmp_path)
    invalid_allowed = allowed.post(
        f"/api/v1/payment-workbook-inputs/{VERSION_ID}/activate",
        json={"idempotency_key": "key", "runtime_profile": "production"},
    )
    assert invalid_allowed.status_code == 422
    assert allowed_transaction.commit_calls == allowed_transaction.rollback_calls == 0
