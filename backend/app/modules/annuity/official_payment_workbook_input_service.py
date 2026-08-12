from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
from os import fstat
from pathlib import Path
from stat import S_ISREG
from tempfile import TemporaryDirectory
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.annuity.models import OfficialPaymentWorkbookInputVersion
from app.modules.annuity.verified_official_payment_workbook import (
    MAX_PACKAGE_BYTES,
    InvalidOfficialPaymentWorkbookError,
    WorkbookStructureSnapshot,
    validate_template,
)

_SOURCE_CLASSIFICATIONS = {"PRODUCTION", "TEST_ONLY"}
_REVIEW_DECISIONS = {"APPROVE": "APPROVED", "REJECT": "REJECTED"}
_HASH_HEX = frozenset("0123456789abcdef")


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterWorkbookInputCommand:
    template_version: str
    template_storage_path: str
    expected_template_hash: str
    upload_proof_storage_path: str
    expected_upload_proof_hash: str
    effective_from: datetime
    effective_to: datetime | None
    source_classification: str
    actor_id: str
    idempotency_key: str
    runtime_profile: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidateWorkbookInputCommand:
    version_id: str
    actor_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewWorkbookInputCommand:
    version_id: str
    decision: str
    reason: str
    actor_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivateWorkbookInputCommand:
    version_id: str
    actor_id: str
    at: datetime
    idempotency_key: str
    runtime_profile: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RetireWorkbookInputCommand:
    version_id: str
    reason: str
    actor_id: str
    at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveWorkbookInputCommand:
    at: datetime
    runtime_profile: str


@dataclass(frozen=True, slots=True, kw_only=True)
class WorkbookInputResult:
    version_id: str
    scope_key: str
    source_classification: str
    template_version: str
    template_storage_path: str
    template_content_hash: str
    upload_proof_storage_path: str
    upload_proof_content_hash: str
    structure_snapshot_hash: str
    workflow_status: str
    activation_status: str
    effective_from: datetime
    effective_to: datetime | None
    supersedes_version_id: str | None
    current_identity_key: str | None
    created_by: str
    validated_by: str | None
    validated_at: datetime | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    activated_by: str | None
    activated_at: datetime | None
    retired_by: str | None
    retired_at: datetime | None
    retirement_reason: str | None
    disposition: str


def _utcnow() -> datetime:
    return datetime.utcnow()


def _invalid(field: str) -> NoReturn:
    raise_business_error(
        "PAYMENT_WORKBOOK_INPUT_INVALID",
        "Invalid official payment workbook input command",
        details={"field": field},
        status_code=400,
    )


def _conflict(reason: str, **details: object) -> NoReturn:
    raise_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFLICT",
        "Official payment workbook input conflict",
        details={"reason": reason, **details},
        status_code=409,
    )


def _config_required(reason: str, **details: object) -> NoReturn:
    raise_business_error(
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        "Official payment workbook input configuration is required",
        details={"reason": reason, **details},
        status_code=409,
    )


def _text(value: object, field: str, limit: int) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > limit
    ):
        _invalid(field)
    return value


def _hash_text(value: object, field: str) -> str:
    result = _text(value, field, 64)
    if len(result) != 64 or any(character not in _HASH_HEX for character in result):
        _invalid(field)
    return result


def _naive_datetime(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.utcoffset() is not None:
        _invalid(field)
    return value


def _runtime_profile(value: object) -> str:
    return _text(value, "runtime_profile", 64)


def _file_hash(path_text: str, *, config_read: bool = False) -> str:
    path = Path(path_text)
    try:
        digest = sha256()
        with path.open("rb") as stream:
            opened = fstat(stream.fileno())
            if not S_ISREG(opened.st_mode):
                raise OSError("managed path is not a regular file")
            before = _file_fingerprint(opened)
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
            after = _file_fingerprint(fstat(stream.fileno()))
            path_after = _file_fingerprint(path.stat())
        if before != after or before != path_after:
            raise OSError("managed file changed while being read")
    except OSError:
        if config_read:
            _config_required("managed_file_unavailable", path=path_text)
        _conflict("managed_file_unavailable", path=path_text)
    return digest.hexdigest()


def _file_fingerprint(stat_result) -> tuple[int, int, int, int, int]:
    return (
        stat_result.st_dev,
        stat_result.st_ino,
        stat_result.st_size,
        stat_result.st_mtime_ns,
        stat_result.st_ctime_ns,
    )


def _canonical_snapshot(snapshot: WorkbookStructureSnapshot) -> str:
    try:
        return json.dumps(
            asdict(snapshot),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _conflict("structure_snapshot_not_canonical")


def _read_snapshot(path_text: str, *, config_read: bool = False) -> tuple[str, str]:
    try:
        snapshot = validate_template(Path(path_text))
    except InvalidOfficialPaymentWorkbookError:
        if config_read:
            _config_required("workbook_structure_invalid", path=path_text)
        _conflict("workbook_structure_invalid", path=path_text)
    canonical = _canonical_snapshot(snapshot)
    return canonical, sha256(canonical.encode("utf-8")).hexdigest()


def _capture_template(
    path_text: str,
    *,
    config_read: bool = False,
) -> tuple[str, str, str]:
    path = Path(path_text)
    try:
        with path.open("rb") as source:
            opened = fstat(source.fileno())
            if not S_ISREG(opened.st_mode):
                raise OSError("managed path is not a regular file")
            if opened.st_size > MAX_PACKAGE_BYTES:
                raise OSError("managed template exceeds the package size limit")
            before = _file_fingerprint(opened)
            with TemporaryDirectory(prefix="fpms-payment-workbook-") as directory:
                immutable_copy = Path(directory) / "template.xlsm"
                digest = sha256()
                copied = 0
                with immutable_copy.open("wb") as target:
                    while chunk := source.read(1024 * 1024):
                        copied += len(chunk)
                        if copied > MAX_PACKAGE_BYTES:
                            raise OSError("managed template exceeds the package size limit")
                        digest.update(chunk)
                        target.write(chunk)
                after_copy = _file_fingerprint(fstat(source.fileno()))
                snapshot, snapshot_hash = _read_snapshot(
                    str(immutable_copy),
                    config_read=config_read,
                )
                after_validation = _file_fingerprint(fstat(source.fileno()))
                path_after = _file_fingerprint(path.stat())
                if not before == after_copy == after_validation == path_after:
                    raise OSError("managed template changed while being validated")
    except OSError:
        if config_read:
            _config_required("managed_file_unavailable", path=path_text)
        _conflict("managed_file_unavailable", path=path_text)
    return digest.hexdigest(), snapshot, snapshot_hash


def _result(row: OfficialPaymentWorkbookInputVersion, disposition: str) -> WorkbookInputResult:
    return WorkbookInputResult(
        version_id=row.id,
        scope_key=row.scope_key,
        source_classification=row.source_classification,
        template_version=row.template_version,
        template_storage_path=row.template_storage_path,
        template_content_hash=row.template_content_hash,
        upload_proof_storage_path=row.upload_proof_storage_path,
        upload_proof_content_hash=row.upload_proof_content_hash,
        structure_snapshot_hash=row.structure_snapshot_hash,
        workflow_status=row.workflow_status,
        activation_status=row.activation_status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        supersedes_version_id=row.supersedes_version_id,
        current_identity_key=row.current_identity_key,
        created_by=row.created_by,
        validated_by=row.validated_by,
        validated_at=row.validated_at,
        reviewed_by=row.reviewed_by,
        reviewed_at=row.reviewed_at,
        activated_by=row.activated_by,
        activated_at=row.activated_at,
        retired_by=row.retired_by,
        retired_at=row.retired_at,
        retirement_reason=row.retirement_reason,
        disposition=disposition,
    )


def _row(transaction: Session, version_id: str) -> OfficialPaymentWorkbookInputVersion:
    with transaction.no_autoflush:
        row = transaction.get(OfficialPaymentWorkbookInputVersion, version_id)
    if row is None:
        _conflict("version_not_found", version_id=version_id)
    return row


def _flush(
    transaction: Session,
    *objects: OfficialPaymentWorkbookInputVersion,
) -> None:
    try:
        transaction.flush(list(objects) or None)
    except IntegrityError:
        _conflict("database_write_conflict")
    except OperationalError as exc:
        if "database is locked" in str(exc.orig).lower():
            _conflict("database_write_locked")
        raise


def _effective(row: OfficialPaymentWorkbookInputVersion, at: datetime) -> bool:
    return row.effective_from <= at and (row.effective_to is None or at < row.effective_to)


def _validate_integrity(
    row: OfficialPaymentWorkbookInputVersion,
    *,
    config_read: bool = False,
) -> None:
    template_hash, snapshot, snapshot_hash = _capture_template(
        row.template_storage_path,
        config_read=config_read,
    )
    proof_hash = _file_hash(row.upload_proof_storage_path, config_read=config_read)
    stored_snapshot_hash = sha256(row.structure_snapshot.encode("utf-8")).hexdigest()
    if (
        template_hash != row.template_content_hash
        or proof_hash != row.upload_proof_content_hash
        or snapshot != row.structure_snapshot
        or snapshot_hash != row.structure_snapshot_hash
        or stored_snapshot_hash != row.structure_snapshot_hash
    ):
        if config_read:
            _config_required("managed_input_integrity_conflict", version_id=row.id)
        _conflict("managed_input_integrity_conflict", version_id=row.id)


def _workflow_tuple_valid(row: OfficialPaymentWorkbookInputVersion) -> bool:
    return (
        row.workflow_status in {"APPROVED", "REJECTED"}
        and row.validated_by is not None
        and row.validated_at is not None
        and bool(row.validation_reason)
        and row.reviewed_by is not None
        and row.reviewed_at is not None
        and bool(row.review_reason)
        and row.reviewed_by != row.created_by
    )


def register_workbook_input(
    transaction: Session,
    command: RegisterWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not RegisterWorkbookInputCommand:
        _invalid("command")
    template_version = _text(command.template_version, "template_version", 128)
    template_path = _text(command.template_storage_path, "template_storage_path", 4096)
    expected_template_hash = _hash_text(
        command.expected_template_hash,
        "expected_template_hash",
    )
    proof_path = _text(command.upload_proof_storage_path, "upload_proof_storage_path", 4096)
    expected_proof_hash = _hash_text(
        command.expected_upload_proof_hash,
        "expected_upload_proof_hash",
    )
    effective_from = _naive_datetime(command.effective_from, "effective_from")
    if command.effective_to is not None:
        effective_to = _naive_datetime(command.effective_to, "effective_to")
        if effective_to <= effective_from:
            _conflict("effective_interval_invalid")
    else:
        effective_to = None
    source = _text(command.source_classification, "source_classification", 24)
    if source not in _SOURCE_CLASSIFICATIONS:
        _invalid("source_classification")
    actor_id = _text(command.actor_id, "actor_id", 36)
    idempotency_key = _text(command.idempotency_key, "idempotency_key", 128)
    runtime_profile = _runtime_profile(command.runtime_profile)
    if source == "TEST_ONLY" and runtime_profile != "test":
        _conflict("test_only_registration_outside_test_profile")

    template_hash, snapshot, snapshot_hash = _capture_template(template_path)
    proof_hash = _file_hash(proof_path)
    if template_hash != expected_template_hash:
        _conflict("template_hash_mismatch")
    if proof_hash != expected_proof_hash:
        _conflict("upload_proof_hash_mismatch")
    with transaction.no_autoflush:
        existing = transaction.scalar(
            select(OfficialPaymentWorkbookInputVersion).where(
                OfficialPaymentWorkbookInputVersion.idempotency_key == idempotency_key
            )
        )
    expected = (
        "GLOBAL",
        source,
        template_version,
        template_path,
        template_hash,
        proof_path,
        proof_hash,
        snapshot,
        snapshot_hash,
        effective_from,
        effective_to,
        actor_id,
    )
    if existing is not None:
        _validate_integrity(existing)
        actual = (
            existing.scope_key,
            existing.source_classification,
            existing.template_version,
            existing.template_storage_path,
            existing.template_content_hash,
            existing.upload_proof_storage_path,
            existing.upload_proof_content_hash,
            existing.structure_snapshot,
            existing.structure_snapshot_hash,
            existing.effective_from,
            existing.effective_to,
            existing.created_by,
        )
        initial_state = (
            existing.workflow_status == "DRAFT"
            and existing.activation_status == "INACTIVE"
            and existing.validated_by is None
            and existing.reviewed_by is None
            and existing.activated_by is None
            and existing.retired_by is None
            and existing.supersedes_version_id is None
            and existing.current_identity_key is None
        )
        if actual != expected or not initial_state:
            _conflict("idempotency_replay_conflict", version_id=existing.id)
        return _result(existing, "REUSED")

    with transaction.no_autoflush:
        version_conflict = transaction.scalar(
            select(OfficialPaymentWorkbookInputVersion.id).where(
                OfficialPaymentWorkbookInputVersion.scope_key == "GLOBAL",
                OfficialPaymentWorkbookInputVersion.template_version == template_version,
            )
        )
    if version_conflict is not None:
        _conflict("template_version_conflict", version_id=version_conflict)

    row = OfficialPaymentWorkbookInputVersion(
        scope_key="GLOBAL",
        source_classification=source,
        template_version=template_version,
        template_storage_path=template_path,
        template_content_hash=template_hash,
        upload_proof_storage_path=proof_path,
        upload_proof_content_hash=proof_hash,
        structure_snapshot=snapshot,
        structure_snapshot_hash=snapshot_hash,
        workflow_status="DRAFT",
        activation_status="INACTIVE",
        effective_from=effective_from,
        effective_to=effective_to,
        idempotency_key=idempotency_key,
        created_by=actor_id,
        updated_by=actor_id,
    )
    transaction.add(row)
    _flush(transaction)
    return _result(row, "CREATED")


def validate_workbook_input(
    transaction: Session,
    command: ValidateWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not ValidateWorkbookInputCommand:
        _invalid("command")
    version_id = _text(command.version_id, "version_id", 36)
    actor_id = _text(command.actor_id, "actor_id", 36)
    row = _row(transaction, version_id)
    _validate_integrity(row)
    if row.workflow_status == "VALIDATED" and row.validated_by == actor_id:
        return _result(row, "REUSED")
    if row.workflow_status != "DRAFT" or row.activation_status != "INACTIVE":
        _conflict("validation_predecessor_conflict", version_id=row.id)
    now = _utcnow()
    row.workflow_status = "VALIDATED"
    row.validated_by = actor_id
    row.validated_at = now
    row.validation_reason = "受控文件、哈希与工作簿结构校验通过"
    row.updated_by = actor_id
    row.updated_at = now
    _flush(transaction)
    return _result(row, "UPDATED")


def review_workbook_input(
    transaction: Session,
    command: ReviewWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not ReviewWorkbookInputCommand:
        _invalid("command")
    version_id = _text(command.version_id, "version_id", 36)
    decision = _text(command.decision, "decision", 16)
    if decision not in _REVIEW_DECISIONS:
        _invalid("decision")
    reason = _text(command.reason, "reason", 2000)
    actor_id = _text(command.actor_id, "actor_id", 36)
    row = _row(transaction, version_id)
    _validate_integrity(row)
    target_status = _REVIEW_DECISIONS[decision]
    if row.activation_status != "INACTIVE":
        _conflict("review_predecessor_conflict", version_id=row.id)
    if (
        row.workflow_status == target_status
        and row.reviewed_by == actor_id
        and row.review_reason == reason
    ):
        return _result(row, "REUSED")
    if row.workflow_status != "VALIDATED":
        _conflict("review_predecessor_conflict", version_id=row.id)
    if actor_id == row.created_by:
        _conflict("reviewer_must_differ_from_uploader", version_id=row.id)
    now = _utcnow()
    row.workflow_status = target_status
    row.reviewed_by = actor_id
    row.reviewed_at = now
    row.review_reason = reason
    row.updated_by = actor_id
    row.updated_at = now
    _flush(transaction)
    return _result(row, "UPDATED")


def activate_workbook_input(
    transaction: Session,
    command: ActivateWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not ActivateWorkbookInputCommand:
        _invalid("command")
    version_id = _text(command.version_id, "version_id", 36)
    actor_id = _text(command.actor_id, "actor_id", 36)
    at = _naive_datetime(command.at, "at")
    idempotency_key = _text(command.idempotency_key, "idempotency_key", 128)
    _runtime_profile(command.runtime_profile)
    row = _row(transaction, version_id)
    _validate_integrity(row)
    if (
        row.activation_status == "ACTIVE"
        and row.current_identity_key == "GLOBAL"
        and row.activated_by == actor_id
        and row.activated_at == at
        and row.idempotency_key == idempotency_key
    ):
        return _result(row, "REUSED")
    if row.source_classification != "PRODUCTION":
        _conflict("test_only_activation_forbidden", version_id=row.id)
    if (
        row.workflow_status != "APPROVED"
        or not _workflow_tuple_valid(row)
        or row.activation_status != "INACTIVE"
        or row.current_identity_key is not None
    ):
        _conflict("activation_predecessor_conflict", version_id=row.id)
    if row.idempotency_key != idempotency_key:
        _conflict("activation_idempotency_conflict", version_id=row.id)
    if not _effective(row, at):
        _conflict("activation_not_effective", version_id=row.id)

    with transaction.no_autoflush:
        current_rows = list(
            transaction.scalars(
                select(OfficialPaymentWorkbookInputVersion).where(
                    OfficialPaymentWorkbookInputVersion.current_identity_key == "GLOBAL"
                )
            ).all()
        )
    if len(current_rows) > 1:
        _conflict("current_identity_multiplicity", count=len(current_rows))
    predecessor = current_rows[0] if current_rows else None
    if predecessor is not None:
        if (
            predecessor.id == row.id
            or predecessor.source_classification != "PRODUCTION"
            or predecessor.workflow_status != "APPROVED"
            or predecessor.activation_status != "ACTIVE"
            or predecessor.current_identity_key != "GLOBAL"
            or predecessor.activated_at is None
            or predecessor.retired_by is not None
            or predecessor.retired_at is not None
            or predecessor.retirement_reason is not None
            or at < predecessor.activated_at
            or row.effective_from < predecessor.effective_from
        ):
            _conflict("active_predecessor_conflict", predecessor_id=predecessor.id)
        _validate_integrity(predecessor)
        predecessor.activation_status = "RETIRED"
        predecessor.retired_by = actor_id
        predecessor.retired_at = at
        predecessor.retirement_reason = f"由工作簿输入版本 {row.id} 替代"
        predecessor.current_identity_key = None
        predecessor.updated_by = actor_id
        predecessor.updated_at = at
        row.supersedes_version_id = predecessor.id
        _flush(transaction, predecessor)
    elif row.supersedes_version_id is not None:
        _conflict("unexpected_predecessor_lineage", version_id=row.id)

    row.activation_status = "ACTIVE"
    row.activated_by = actor_id
    row.activated_at = at
    row.current_identity_key = "GLOBAL"
    row.updated_by = actor_id
    row.updated_at = at
    _flush(transaction)
    return _result(row, "UPDATED")


def retire_workbook_input(
    transaction: Session,
    command: RetireWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not RetireWorkbookInputCommand:
        _invalid("command")
    version_id = _text(command.version_id, "version_id", 36)
    reason = _text(command.reason, "reason", 2000)
    actor_id = _text(command.actor_id, "actor_id", 36)
    at = _naive_datetime(command.at, "at")
    idempotency_key = _text(command.idempotency_key, "idempotency_key", 128)
    row = _row(transaction, version_id)
    _validate_integrity(row)
    if (
        row.activation_status == "RETIRED"
        and row.retired_by == actor_id
        and row.retired_at == at
        and row.retirement_reason == reason
        and row.idempotency_key == idempotency_key
    ):
        return _result(row, "REUSED")
    if (
        row.source_classification != "PRODUCTION"
        or row.workflow_status != "APPROVED"
        or row.activation_status != "ACTIVE"
        or row.current_identity_key != "GLOBAL"
        or row.activated_at is None
    ):
        _conflict("retirement_predecessor_conflict", version_id=row.id)
    if row.idempotency_key != idempotency_key:
        _conflict("retirement_idempotency_conflict", version_id=row.id)
    if at < row.activated_at:
        _conflict("retirement_before_activation", version_id=row.id)
    row.activation_status = "RETIRED"
    row.retired_by = actor_id
    row.retired_at = at
    row.retirement_reason = reason
    row.current_identity_key = None
    row.updated_by = actor_id
    row.updated_at = at
    _flush(transaction)
    return _result(row, "UPDATED")


def _resolution_tuple_valid(
    row: OfficialPaymentWorkbookInputVersion,
    *,
    test_profile: bool,
) -> bool:
    if row.scope_key != "GLOBAL" or not _workflow_tuple_valid(row):
        return False
    if test_profile:
        return (
            row.source_classification == "TEST_ONLY"
            and row.workflow_status == "APPROVED"
            and row.activation_status == "INACTIVE"
            and row.activated_by is None
            and row.activated_at is None
            and row.retired_by is None
            and row.retired_at is None
            and row.retirement_reason is None
            and row.current_identity_key is None
        )
    return (
        row.source_classification == "PRODUCTION"
        and row.workflow_status == "APPROVED"
        and row.activation_status == "ACTIVE"
        and row.activated_by is not None
        and row.activated_at is not None
        and row.retired_by is None
        and row.retired_at is None
        and row.retirement_reason is None
        and row.current_identity_key == "GLOBAL"
    )


def resolve_workbook_input(
    transaction: Session,
    command: ResolveWorkbookInputCommand,
) -> WorkbookInputResult:
    if type(command) is not ResolveWorkbookInputCommand:
        _invalid("command")
    at = _naive_datetime(command.at, "at")
    runtime_profile = _runtime_profile(command.runtime_profile)
    test_profile = runtime_profile == "test"
    with transaction.no_autoflush:
        rows = list(
            transaction.scalars(
                select(OfficialPaymentWorkbookInputVersion).where(
                    OfficialPaymentWorkbookInputVersion.source_classification
                    == ("TEST_ONLY" if test_profile else "PRODUCTION"),
                    OfficialPaymentWorkbookInputVersion.workflow_status == "APPROVED",
                    OfficialPaymentWorkbookInputVersion.activation_status
                    == ("INACTIVE" if test_profile else "ACTIVE"),
                )
            ).all()
        )
    eligible = [row for row in rows if _effective(row, at)]
    if len(eligible) != 1:
        _config_required(
            "eligible_version_count",
            source_classification="TEST_ONLY" if test_profile else "PRODUCTION",
            count=len(eligible),
        )
    row = eligible[0]
    if not _resolution_tuple_valid(row, test_profile=test_profile):
        _config_required("stored_state_tuple_invalid", version_id=row.id)
    _validate_integrity(row, config_read=True)
    return _result(row, "RESOLVED")
