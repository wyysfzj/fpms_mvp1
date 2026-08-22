from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
from shutil import copyfile

import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.errors import BusinessError
from app.db.base import Base
from app.modules.annuity.models import OfficialPaymentWorkbookInputVersion
from app.modules.annuity.official_payment_workbook_input_service import (
    ActivateWorkbookInputCommand,
    RegisterWorkbookInputCommand,
    ResolveWorkbookInputCommand,
    RetireWorkbookInputCommand,
    ReviewWorkbookInputCommand,
    ValidateWorkbookInputCommand,
    activate_workbook_input,
    register_workbook_input,
    resolve_workbook_input,
    retire_workbook_input,
    review_workbook_input,
    validate_workbook_input,
)
from app.modules.annuity.verified_official_payment_workbook import MAX_PACKAGE_BYTES
from app.modules.auth.models import T_User

NOW = datetime(2026, 8, 13, 9, 0)
LATER = NOW + timedelta(days=365)
USERS = tuple(f"00000000-0000-4000-8000-{index:012d}" for index in range(1, 7))
FIXTURE = Path(__file__).parent / "fixtures" / "v8_verified_official_payment_template.xlsm"


@pytest.fixture
def transaction() -> Session:
    engine = create_engine(
        "sqlite://",
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record) -> None:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(
        engine,
        tables=[T_User.__table__, OfficialPaymentWorkbookInputVersion.__table__],
    )
    with engine.begin() as connection:
        connection.execute(
            T_User.__table__.insert(),
            [
                {
                    "id": user_id,
                    "username": f"workbook-service-user-{index}",
                    "password_hash": "test-only",
                }
                for index, user_id in enumerate(USERS, start=1)
            ],
        )
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def managed_files(tmp_path: Path) -> tuple[Path, Path]:
    template = tmp_path / "managed" / "templates" / "official.xlsm"
    proof = tmp_path / "managed" / "proofs" / "upload-proof.json"
    template.parent.mkdir(parents=True)
    proof.parent.mkdir(parents=True)
    copyfile(FIXTURE, template)
    proof.write_bytes(b'{"controlled_upload":true,"source":"TEST_ONLY"}')
    return template, proof


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _register_command(
    managed_files: tuple[Path, Path],
    *,
    version: str = "2026.08",
    source: str = "PRODUCTION",
    runtime_profile: str = "production",
    actor: str = USERS[0],
    key: str = "workbook-register-2026-08",
) -> RegisterWorkbookInputCommand:
    template, proof = managed_files
    return RegisterWorkbookInputCommand(
        template_version=version,
        template_storage_path=str(template),
        expected_template_hash=_hash(template),
        upload_proof_storage_path=str(proof),
        expected_upload_proof_hash=_hash(proof),
        effective_from=NOW,
        effective_to=LATER,
        source_classification=source,
        actor_id=actor,
        idempotency_key=key,
        runtime_profile=runtime_profile,
    )


def _register_validate_review(
    transaction: Session,
    managed_files: tuple[Path, Path],
    *,
    version: str = "2026.08",
    source: str = "PRODUCTION",
    runtime_profile: str = "production",
    key: str = "workbook-register-2026-08",
) -> tuple[RegisterWorkbookInputCommand, str]:
    command = _register_command(
        managed_files,
        version=version,
        source=source,
        runtime_profile=runtime_profile,
        key=key,
    )
    created = register_workbook_input(transaction, command)
    validated = validate_workbook_input(
        transaction,
        ValidateWorkbookInputCommand(version_id=created.version_id, actor_id=USERS[1]),
    )
    assert validated.workflow_status == "VALIDATED"
    approved = review_workbook_input(
        transaction,
        ReviewWorkbookInputCommand(
            version_id=created.version_id,
            decision="APPROVE",
            reason="独立复核文件、来源和结构均一致",
            actor_id=USERS[2],
        ),
    )
    assert approved.workflow_status == "APPROVED"
    return command, created.version_id


def _count(transaction: Session) -> int:
    return transaction.scalar(select(func.count(OfficialPaymentWorkbookInputVersion.id))) or 0


def _expect_business_error(code: str, status: int, operation) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        operation()
    assert captured.value.code == code
    assert captured.value.status_code == status
    return captured.value


def test_register_streams_hashes_stores_canonical_snapshot_and_replays_exactly(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    command = _register_command(managed_files)
    created = register_workbook_input(transaction, command)

    assert created.disposition == "CREATED"
    assert created.scope_key == "GLOBAL"
    assert created.workflow_status == "DRAFT"
    assert created.activation_status == "INACTIVE"
    assert created.template_content_hash == command.expected_template_hash
    assert created.upload_proof_content_hash == command.expected_upload_proof_hash
    assert len(created.structure_snapshot_hash) == 64
    row = transaction.get(OfficialPaymentWorkbookInputVersion, created.version_id)
    assert row is not None
    assert row.structure_snapshot.startswith('{"column_widths":')
    assert sha256(row.structure_snapshot.encode()).hexdigest() == row.structure_snapshot_hash

    replay = register_workbook_input(transaction, command)
    assert replay.disposition == "REUSED"
    assert replay.version_id == created.version_id
    assert _count(transaction) == 1

    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(transaction, replace(command, template_version="changed")),
    )
    assert _count(transaction) == 1


@pytest.mark.parametrize(
    "mutator",
    [
        lambda command: replace(command, expected_template_hash="0" * 64),
        lambda command: replace(command, expected_upload_proof_hash="0" * 64),
        lambda command: replace(command, effective_to=command.effective_from),
        lambda command: replace(command, source_classification="TEST_ONLY"),
        lambda command: replace(command, runtime_profile="test", source_classification="UNKNOWN"),
    ],
)
def test_registration_failures_leave_no_row(
    transaction: Session,
    managed_files: tuple[Path, Path],
    mutator,
) -> None:
    command = mutator(_register_command(managed_files))
    error = _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT"
        if command.source_classification in {"PRODUCTION", "TEST_ONLY"}
        else "PAYMENT_WORKBOOK_INPUT_INVALID",
        409 if command.source_classification in {"PRODUCTION", "TEST_ONLY"} else 400,
        lambda: register_workbook_input(transaction, command),
    )
    assert error.details is not None
    assert _count(transaction) == 0


def test_missing_or_malformed_managed_files_fail_before_write(
    transaction: Session,
    managed_files: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    command = _register_command(managed_files)
    missing = tmp_path / "missing.xlsm"
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(
            transaction,
            replace(command, template_storage_path=str(missing)),
        ),
    )
    malformed = tmp_path / "malformed.xlsm"
    malformed.write_bytes(b"not an OOXML workbook")
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(
            transaction,
            replace(
                command,
                template_storage_path=str(malformed),
                expected_template_hash=_hash(malformed),
            ),
        ),
    )
    assert _count(transaction) == 0


def test_registration_rejects_template_replaced_between_hash_and_structure_validation(
    transaction: Session,
    managed_files: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.annuity import official_payment_workbook_input_service as service

    template, _ = managed_files
    command = _register_command(managed_files)
    replacement = template.with_name("replacement.xlsm")
    replacement.write_bytes(FIXTURE.read_bytes() + b"different-but-structurally-valid-bytes")
    real_validate = service.validate_template

    def replace_during_validation(path: Path):
        template.write_bytes(replacement.read_bytes())
        return real_validate(path)

    monkeypatch.setattr(service, "validate_template", replace_during_validation)
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(transaction, command),
    )
    assert _count(transaction) == 0


def test_registration_rejects_non_regular_managed_file(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    command = _register_command(managed_files)
    empty_hash = sha256(b"").hexdigest()
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(
            transaction,
            replace(
                command,
                upload_proof_storage_path="/dev/null",
                expected_upload_proof_hash=empty_hash,
            ),
        ),
    )
    assert _count(transaction) == 0


def test_oversized_template_is_rejected_before_temporary_copy(
    transaction: Session,
    managed_files: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from app.modules.annuity import official_payment_workbook_input_service as service

    oversized = tmp_path / "oversized.xlsm"
    with oversized.open("wb") as stream:
        stream.truncate(MAX_PACKAGE_BYTES + 1)
    command = replace(
        _register_command(managed_files),
        template_storage_path=str(oversized),
        expected_template_hash="0" * 64,
    )

    def temporary_copy_must_not_start(*_args, **_kwargs):
        raise AssertionError("temporary copy started before size rejection")

    monkeypatch.setattr(service, "TemporaryDirectory", temporary_copy_must_not_start)
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(transaction, command),
    )
    assert _count(transaction) == 0


def test_registration_maps_unique_flush_failure_to_conflict_and_caller_rolls_back(
    transaction: Session,
    managed_files: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command = _register_command(managed_files)
    real_flush = transaction.flush

    def conflicting_flush(*_args, **_kwargs) -> None:
        raise IntegrityError("INSERT", {}, Exception("unique constraint"))

    monkeypatch.setattr(transaction, "flush", conflicting_flush)
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: register_workbook_input(transaction, command),
    )
    monkeypatch.setattr(transaction, "flush", real_flush)
    transaction.rollback()
    assert _count(transaction) == 0


def test_activation_maps_sqlite_lock_to_conflict_and_caller_rollback_preserves_state(
    transaction: Session,
    managed_files: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    command, version_id = _register_validate_review(transaction, managed_files)
    transaction.commit()
    real_flush = transaction.flush

    def locked_flush(*_args, **_kwargs) -> None:
        raise OperationalError("UPDATE", {}, Exception("database is locked"))

    monkeypatch.setattr(transaction, "flush", locked_flush)
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: activate_workbook_input(
            transaction,
            ActivateWorkbookInputCommand(
                version_id=version_id,
                actor_id=USERS[3],
                at=NOW + timedelta(hours=1),
                idempotency_key=command.idempotency_key,
                runtime_profile="production",
            ),
        ),
    )
    monkeypatch.setattr(transaction, "flush", real_flush)
    transaction.rollback()
    transaction.expire_all()
    row = transaction.get(OfficialPaymentWorkbookInputVersion, version_id)
    assert row is not None
    assert row.activation_status == "INACTIVE"
    assert row.current_identity_key is None


def test_validation_rechecks_files_and_review_requires_a_second_person(
    transaction: Session,
    managed_files: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.annuity import official_payment_workbook_input_service as service

    monkeypatch.setattr(service, "_utcnow", lambda: NOW + timedelta(minutes=5))
    created = register_workbook_input(transaction, _register_command(managed_files))
    validated = validate_workbook_input(
        transaction,
        ValidateWorkbookInputCommand(version_id=created.version_id, actor_id=USERS[1]),
    )
    assert validated.workflow_status == "VALIDATED"
    assert validated.validated_by == USERS[1]
    assert validated.validated_at == NOW + timedelta(minutes=5)
    assert (
        validate_workbook_input(
            transaction,
            ValidateWorkbookInputCommand(version_id=created.version_id, actor_id=USERS[1]),
        ).disposition
        == "REUSED"
    )

    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: review_workbook_input(
            transaction,
            ReviewWorkbookInputCommand(
                version_id=created.version_id,
                decision="APPROVE",
                reason="同一上传人不得复核",
                actor_id=USERS[0],
            ),
        ),
    )
    approved = review_workbook_input(
        transaction,
        ReviewWorkbookInputCommand(
            version_id=created.version_id,
            decision="APPROVE",
            reason="独立复核通过",
            actor_id=USERS[2],
        ),
    )
    assert approved.workflow_status == "APPROVED"
    assert approved.reviewed_by == USERS[2]
    assert (
        review_workbook_input(
            transaction,
            ReviewWorkbookInputCommand(
                version_id=created.version_id,
                decision="APPROVE",
                reason="独立复核通过",
                actor_id=USERS[2],
            ),
        ).disposition
        == "REUSED"
    )


def test_validation_detects_changed_managed_bytes_without_state_write(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    created = register_workbook_input(transaction, _register_command(managed_files))
    _, proof = managed_files
    proof.write_bytes(b"changed after registration")

    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: validate_workbook_input(
            transaction,
            ValidateWorkbookInputCommand(version_id=created.version_id, actor_id=USERS[1]),
        ),
    )
    row = transaction.get(OfficialPaymentWorkbookInputVersion, created.version_id)
    assert row is not None
    assert row.workflow_status == "DRAFT"
    assert row.validated_by is None


def test_production_activation_resolution_and_retirement_are_fail_closed(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    command, version_id = _register_validate_review(transaction, managed_files)
    activated = activate_workbook_input(
        transaction,
        ActivateWorkbookInputCommand(
            version_id=version_id,
            actor_id=USERS[3],
            at=NOW + timedelta(hours=1),
            idempotency_key=command.idempotency_key,
            runtime_profile="production",
        ),
    )
    assert activated.activation_status == "ACTIVE"
    assert activated.current_identity_key == "GLOBAL"
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: review_workbook_input(
            transaction,
            ReviewWorkbookInputCommand(
                version_id=version_id,
                decision="APPROVE",
                reason="独立复核文件、来源和结构均一致",
                actor_id=USERS[2],
            ),
        ),
    )
    unchanged = transaction.get(OfficialPaymentWorkbookInputVersion, version_id)
    assert unchanged is not None
    assert unchanged.activation_status == "ACTIVE"
    assert unchanged.current_identity_key == "GLOBAL"
    resolved = resolve_workbook_input(
        transaction,
        ResolveWorkbookInputCommand(at=NOW + timedelta(days=1), runtime_profile="production"),
    )
    assert resolved.version_id == version_id
    assert resolved.disposition == "RESOLVED"

    retired = retire_workbook_input(
        transaction,
        RetireWorkbookInputCommand(
            version_id=version_id,
            reason="机构管理员撤销当前版本",
            actor_id=USERS[4],
            at=NOW + timedelta(days=2),
            idempotency_key=command.idempotency_key,
        ),
    )
    assert retired.activation_status == "RETIRED"
    assert retired.current_identity_key is None
    assert (
        retire_workbook_input(
            transaction,
            RetireWorkbookInputCommand(
                version_id=version_id,
                reason="机构管理员撤销当前版本",
                actor_id=USERS[4],
                at=NOW + timedelta(days=2),
                idempotency_key=command.idempotency_key,
            ),
        ).disposition
        == "REUSED"
    )
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        409,
        lambda: resolve_workbook_input(
            transaction,
            ResolveWorkbookInputCommand(at=NOW + timedelta(days=3), runtime_profile="production"),
        ),
    )


def test_activation_retires_exact_predecessor_and_records_lineage(
    transaction: Session,
    managed_files: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    first_command, first_id = _register_validate_review(transaction, managed_files)
    activate_workbook_input(
        transaction,
        ActivateWorkbookInputCommand(
            version_id=first_id,
            actor_id=USERS[3],
            at=NOW + timedelta(hours=1),
            idempotency_key=first_command.idempotency_key,
            runtime_profile="production",
        ),
    )

    second_template = tmp_path / "managed" / "templates" / "official-v2.xlsm"
    second_proof = tmp_path / "managed" / "proofs" / "upload-proof-v2.json"
    copyfile(FIXTURE, second_template)
    second_proof.write_bytes(b'{"controlled_upload":true,"version":2}')
    second_files = (second_template, second_proof)
    second_command, second_id = _register_validate_review(
        transaction,
        second_files,
        version="2026.09",
        key="workbook-register-2026-09",
    )
    second = activate_workbook_input(
        transaction,
        ActivateWorkbookInputCommand(
            version_id=second_id,
            actor_id=USERS[3],
            at=NOW + timedelta(days=2),
            idempotency_key=second_command.idempotency_key,
            runtime_profile="production",
        ),
    )
    first = transaction.get(OfficialPaymentWorkbookInputVersion, first_id)
    assert first is not None
    assert first.activation_status == "RETIRED"
    assert first.retirement_reason == f"由工作簿输入版本 {second_id} 替代"
    assert second.supersedes_version_id == first_id
    assert (
        resolve_workbook_input(
            transaction,
            ResolveWorkbookInputCommand(at=NOW + timedelta(days=3), runtime_profile="production"),
        ).version_id
        == second_id
    )


def test_test_only_isolated_resolution_never_activates_or_becomes_current(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    command, version_id = _register_validate_review(
        transaction,
        managed_files,
        source="TEST_ONLY",
        runtime_profile="test",
    )
    resolved = resolve_workbook_input(
        transaction,
        ResolveWorkbookInputCommand(at=NOW + timedelta(days=1), runtime_profile="test"),
    )
    assert resolved.version_id == version_id
    assert resolved.source_classification == "TEST_ONLY"
    assert resolved.activation_status == "INACTIVE"
    assert resolved.current_identity_key is None

    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        409,
        lambda: activate_workbook_input(
            transaction,
            ActivateWorkbookInputCommand(
                version_id=version_id,
                actor_id=USERS[3],
                at=NOW + timedelta(days=1),
                idempotency_key=command.idempotency_key,
                runtime_profile="test",
            ),
        ),
    )
    row = transaction.get(OfficialPaymentWorkbookInputVersion, version_id)
    assert row is not None
    assert row.activation_status == "INACTIVE"
    assert row.current_identity_key is None


def test_test_resolution_rejects_ambiguity_and_production_rejects_test_only(
    transaction: Session,
    managed_files: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    _register_validate_review(
        transaction,
        managed_files,
        source="TEST_ONLY",
        runtime_profile="test",
    )
    second_template = tmp_path / "second.xlsm"
    second_proof = tmp_path / "second-proof.json"
    copyfile(FIXTURE, second_template)
    second_proof.write_bytes(b"second test-only proof")
    _register_validate_review(
        transaction,
        (second_template, second_proof),
        version="2026.09",
        source="TEST_ONLY",
        runtime_profile="test",
        key="workbook-register-test-2",
    )
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        409,
        lambda: resolve_workbook_input(
            transaction,
            ResolveWorkbookInputCommand(at=NOW + timedelta(days=1), runtime_profile="test"),
        ),
    )
    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        409,
        lambda: resolve_workbook_input(
            transaction,
            ResolveWorkbookInputCommand(at=NOW + timedelta(days=1), runtime_profile="production"),
        ),
    )


def test_resolver_rechecks_current_file_integrity_without_writing(
    transaction: Session,
    managed_files: tuple[Path, Path],
) -> None:
    command, version_id = _register_validate_review(transaction, managed_files)
    activate_workbook_input(
        transaction,
        ActivateWorkbookInputCommand(
            version_id=version_id,
            actor_id=USERS[3],
            at=NOW + timedelta(hours=1),
            idempotency_key=command.idempotency_key,
            runtime_profile="production",
        ),
    )
    _, proof = managed_files
    proof.write_bytes(b"tampered after activation")

    _expect_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        409,
        lambda: resolve_workbook_input(
            transaction,
            ResolveWorkbookInputCommand(at=NOW + timedelta(days=1), runtime_profile="production"),
        ),
    )
    row = transaction.get(OfficialPaymentWorkbookInputVersion, version_id)
    assert row is not None
    assert row.activation_status == "ACTIVE"
    assert row.current_identity_key == "GLOBAL"
