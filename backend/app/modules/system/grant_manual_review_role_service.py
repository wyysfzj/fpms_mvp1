from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_Role, T_User, T_UserRole
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateReadResult,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)
from app.modules.system.models import GrantManualReviewRoleConfig


class GrantManualReviewRoleDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishGrantManualReviewRoleConfigCommand:
    official_copy_acquirer_role_id: str
    first_verifier_role_id: str
    second_verifier_role_id: str
    manual_review_proposer_role_id: str
    manual_review_second_reviewer_role_id: str
    config_version: str
    effective_from: datetime
    effective_to: datetime | None
    confirmed_by: str
    published_at: datetime
    expected_current_config_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeGrantManualReviewRoleConfigCommand:
    config_version: str
    effective_from: datetime
    confirmed_by: str
    published_at: datetime
    expected_current_config_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveGrantManualReviewRoleConfigCommand:
    as_of: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantManualReviewRoleConfigResult:
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantManualReviewRoleDisposition


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantManualReviewRoleResolution:
    gate_id: str
    config_id: str
    config_snapshot_hash: str
    official_copy_acquirer_role_id: str
    first_verifier_role_id: str
    second_verifier_role_id: str
    manual_review_proposer_role_id: str
    manual_review_second_reviewer_role_id: str
    effective_from: datetime
    effective_to: datetime | None


_GATE_CODE = "DG-GRANT-MANUAL-REVIEW"
_SCOPE_KEY = "GLOBAL"
_DECISION_VALUE = "APPROVED_POLICY"
_DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
_SCHEMA = "FPMS_GRANT_MANUAL_REVIEW_ROLE_CONFIG_V1"
_CURRENT_IDENTITY = f"{_GATE_CODE}|{_SCOPE_KEY}"
_ROLE_FIELDS = (
    "official_copy_acquirer_role_id",
    "first_verifier_role_id",
    "second_verifier_role_id",
    "manual_review_proposer_role_id",
    "manual_review_second_reviewer_role_id",
)


def _invalid(field: str) -> None:
    raise_business_error(
        "GRANT_MANUAL_REVIEW_ROLE_INPUT_INVALID",
        "Invalid grant manual-review role configuration input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "GRANT_MANUAL_REVIEW_ROLE_CONFLICT",
        "Grant manual-review role configuration conflict",
        status_code=409,
    )


def _validate_string(value: object, field: str, limit: int) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > limit
    ):
        _invalid(field)
    return value


def _validate_uuid(value: object, field: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if type(value) is not str:
        _invalid(field)
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _invalid(field)
    if str(parsed) != value:
        _invalid(field)
    return value


def _validate_datetime(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.utcoffset() is not None:
        _invalid(field)
    return value


def _validate_interval(start: datetime, end: datetime | None) -> None:
    if end is not None:
        _validate_datetime(end, "effective_to")
        if end <= start:
            _invalid("effective_to")


def _validate_publish(
    command: object,
) -> PublishGrantManualReviewRoleConfigCommand:
    if type(command) is not PublishGrantManualReviewRoleConfigCommand:
        _invalid("command")
    for field in _ROLE_FIELDS:
        _validate_uuid(getattr(command, field), field)
    _validate_string(command.config_version, "config_version", 128)
    start = _validate_datetime(command.effective_from, "effective_from")
    _validate_interval(start, command.effective_to)
    _validate_uuid(command.confirmed_by, "confirmed_by")
    _validate_datetime(command.published_at, "published_at")
    _validate_uuid(
        command.expected_current_config_id,
        "expected_current_config_id",
        optional=True,
    )
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_revoke(
    command: object,
) -> RevokeGrantManualReviewRoleConfigCommand:
    if type(command) is not RevokeGrantManualReviewRoleConfigCommand:
        _invalid("command")
    _validate_string(command.config_version, "config_version", 128)
    _validate_datetime(command.effective_from, "effective_from")
    _validate_uuid(command.confirmed_by, "confirmed_by")
    _validate_datetime(command.published_at, "published_at")
    _validate_uuid(command.expected_current_config_id, "expected_current_config_id")
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_resolve(
    command: object,
) -> ResolveGrantManualReviewRoleConfigCommand:
    if type(command) is not ResolveGrantManualReviewRoleConfigCommand:
        _invalid("command")
    _validate_datetime(command.as_of, "as_of")
    return command


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict()
    return transaction


def _canonical_json(value: dict[str, object]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _timestamp(value: datetime) -> str:
    return value.isoformat(timespec="microseconds")


def _snapshot(
    *,
    role_ids: tuple[str, str, str, str, str],
    config_version: str,
    config_status: str,
    effective_from: datetime,
    effective_to: datetime | None,
    confirmed_by: str,
    published_at: datetime,
    expected_current_config_id: str | None,
) -> str:
    return _canonical_json(
        {
            "config_status": config_status,
            "config_version": config_version,
            "confirmed_by": confirmed_by,
            "effective_from": _timestamp(effective_from),
            "effective_to": _timestamp(effective_to) if effective_to is not None else None,
            "expected_current_config_id": expected_current_config_id,
            "first_verifier_role_id": role_ids[1],
            "gate_code": _GATE_CODE,
            "manual_review_proposer_role_id": role_ids[3],
            "manual_review_second_reviewer_role_id": role_ids[4],
            "official_copy_acquirer_role_id": role_ids[0],
            "published_at": _timestamp(published_at),
            "schema": _SCHEMA,
            "scope_key": _SCOPE_KEY,
            "second_verifier_role_id": role_ids[2],
        }
    )


def _row_role_ids(row: GrantManualReviewRoleConfig) -> tuple[str, str, str, str, str]:
    return tuple(getattr(row, field) for field in _ROLE_FIELDS)


def _validate_canonical(row: GrantManualReviewRoleConfig) -> None:
    if (
        type(row.effective_from) is not datetime
        or row.effective_from.utcoffset() is not None
        or type(row.published_at) is not datetime
        or row.published_at.utcoffset() is not None
        or (
            row.effective_to is not None
            and (
                type(row.effective_to) is not datetime
                or row.effective_to.utcoffset() is not None
                or row.effective_to <= row.effective_from
            )
        )
    ):
        _conflict()
    expected = _snapshot(
        role_ids=_row_role_ids(row),
        config_version=row.config_version,
        config_status=row.config_status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        confirmed_by=row.confirmed_by,
        published_at=row.published_at,
        expected_current_config_id=row.supersedes_config_id,
    )
    if (
        row.gate_code != _GATE_CODE
        or row.scope_key != _SCOPE_KEY
        or row.config_status not in {"ACTIVE", "REVOKED"}
        or row.current_identity_key not in {None, _CURRENT_IDENTITY}
        or row.config_snapshot != expected
        or row.config_snapshot_hash != _hash(expected)
    ):
        _conflict()


def _result(
    row: GrantManualReviewRoleConfig,
    disposition: GrantManualReviewRoleDisposition,
) -> GrantManualReviewRoleConfigResult:
    return GrantManualReviewRoleConfigResult(
        config_id=row.id,
        config_status=row.config_status,
        config_snapshot_hash=row.config_snapshot_hash,
        current_identity_key=row.current_identity_key,
        disposition=disposition,
    )


def _one_or_none(rows: list[GrantManualReviewRoleConfig]) -> GrantManualReviewRoleConfig | None:
    if len(rows) > 1:
        _conflict()
    return rows[0] if rows else None


def _gate(transaction: Session, as_of: datetime) -> DecisionGateReadResult:
    try:
        result = resolve_decision_gate(
            ResolveDecisionGateCommand(
                gate_code=DecisionGateCode.GRANT_MANUAL_REVIEW,
                scope_key=_SCOPE_KEY,
                as_of=as_of,
            ),
            transaction,
        )
    except BusinessError:
        _conflict()
    if (
        result.gate_code is not DecisionGateCode.GRANT_MANUAL_REVIEW
        or result.resolved_scope_key != _SCOPE_KEY
        or result.decision_value != _DECISION_VALUE
        or result.source_reference != _DECISION_SOURCE
        or result.source_version != _DECISION_VERSION
    ):
        _conflict()
    return result


def _user_exists(transaction: Session, user_id: str) -> None:
    if transaction.scalar(select(T_User.id).where(T_User.id == user_id)) is None:
        _conflict()


def _active_role_members(
    transaction: Session,
    role_ids: tuple[str, str, str, str, str],
) -> dict[str, set[str]]:
    unique_ids = set(role_ids)
    existing = set(
        transaction.scalars(select(T_Role.id).where(T_Role.id.in_(unique_ids))).all()
    )
    if existing != unique_ids:
        _conflict()
    members = {role_id: set() for role_id in unique_ids}
    rows = transaction.execute(
        select(T_UserRole.role_id, T_UserRole.user_id)
        .join(T_User, T_User.id == T_UserRole.user_id)
        .where(T_UserRole.role_id.in_(unique_ids), T_User.is_active.is_(True))
    ).all()
    for role_id, user_id in rows:
        members[role_id].add(user_id)
    if any(not members[role_id] for role_id in unique_ids):
        _conflict()
    return members


def _distinct_pair_exists(first: set[str], second: set[str]) -> bool:
    return any(first_user != second_user for first_user in first for second_user in second)


def _validate_personnel_ready(
    transaction: Session,
    role_ids: tuple[str, str, str, str, str],
) -> None:
    members = _active_role_members(transaction, role_ids)
    if not _distinct_pair_exists(members[role_ids[1]], members[role_ids[2]]):
        _conflict()
    if not _distinct_pair_exists(members[role_ids[3]], members[role_ids[4]]):
        _conflict()


def _replay(
    row: GrantManualReviewRoleConfig,
    expected_snapshot: str,
) -> GrantManualReviewRoleConfigResult:
    _validate_canonical(row)
    if row.config_snapshot != expected_snapshot:
        _conflict()
    return _result(row, GrantManualReviewRoleDisposition.REUSED)


def _current(transaction: Session) -> GrantManualReviewRoleConfig | None:
    return _one_or_none(
        list(
            transaction.scalars(
                select(GrantManualReviewRoleConfig).where(
                    GrantManualReviewRoleConfig.current_identity_key == _CURRENT_IDENTITY
                )
            )
        )
    )


def _validate_predecessor_chain(
    transaction: Session,
    row: GrantManualReviewRoleConfig,
) -> None:
    if row.config_status == "REVOKED" and (
        row.supersedes_config_id is None or row.effective_to is not None
    ):
        _conflict()
    seen = {row.id}
    current = row
    while current.supersedes_config_id is not None:
        predecessor_id = current.supersedes_config_id
        if predecessor_id in seen:
            _conflict()
        predecessor = transaction.get(GrantManualReviewRoleConfig, predecessor_id)
        if predecessor is None:
            _conflict()
        _validate_canonical(predecessor)
        if predecessor.current_identity_key is not None:
            _conflict()
        if current.config_status == "REVOKED" and _row_role_ids(current) != _row_role_ids(
            predecessor
        ):
            _conflict()
        seen.add(predecessor_id)
        current = predecessor


def _applicable(start: datetime, end: datetime | None, as_of: datetime) -> bool:
    return start <= as_of and (end is None or as_of < end)


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def publish_grant_manual_review_role_config(
    command: PublishGrantManualReviewRoleConfigCommand,
    transaction: Session,
) -> GrantManualReviewRoleConfigResult:
    command = _validate_publish(command)
    transaction = _validate_transaction(transaction)
    _gate(transaction, command.published_at)
    role_ids = tuple(getattr(command, field) for field in _ROLE_FIELDS)
    snapshot = _snapshot(
        role_ids=role_ids,
        config_version=command.config_version,
        config_status="ACTIVE",
        effective_from=command.effective_from,
        effective_to=command.effective_to,
        confirmed_by=command.confirmed_by,
        published_at=command.published_at,
        expected_current_config_id=command.expected_current_config_id,
    )
    with transaction.no_autoflush:
        _user_exists(transaction, command.confirmed_by)
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantManualReviewRoleConfig).where(
                        GrantManualReviewRoleConfig.idempotency_key == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            result = _replay(replay, snapshot)
            _validate_predecessor_chain(transaction, replay)
            _validate_personnel_ready(transaction, _row_role_ids(replay))
            return result
        _validate_personnel_ready(transaction, role_ids)
        current = _current(transaction)
        actual_current_id = current.id if current is not None else None
        if actual_current_id != command.expected_current_config_id:
            _conflict()
        if current is not None:
            _validate_canonical(current)
            _validate_predecessor_chain(transaction, current)

    row = GrantManualReviewRoleConfig(
        id=str(uuid4()),
        gate_code=_GATE_CODE,
        scope_key=_SCOPE_KEY,
        official_copy_acquirer_role_id=role_ids[0],
        first_verifier_role_id=role_ids[1],
        second_verifier_role_id=role_ids[2],
        manual_review_proposer_role_id=role_ids[3],
        manual_review_second_reviewer_role_id=role_ids[4],
        config_version=command.config_version,
        config_status="ACTIVE",
        effective_from=command.effective_from,
        effective_to=command.effective_to,
        confirmed_by=command.confirmed_by,
        published_at=command.published_at,
        supersedes_config_id=command.expected_current_config_id,
        config_snapshot=snapshot,
        config_snapshot_hash=_hash(snapshot),
        idempotency_key=command.idempotency_key,
        current_identity_key=_CURRENT_IDENTITY,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            if current is not None:
                result = transaction.execute(
                    update(GrantManualReviewRoleConfig)
                    .where(
                        GrantManualReviewRoleConfig.id
                        == command.expected_current_config_id,
                        GrantManualReviewRoleConfig.current_identity_key == _CURRENT_IDENTITY,
                    )
                    .values(current_identity_key=None)
                )
                if result.rowcount != 1:
                    _conflict()
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantManualReviewRoleConfig).where(
                            GrantManualReviewRoleConfig.idempotency_key
                            == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                return _replay(replay, snapshot)
        _conflict()
    return _result(row, GrantManualReviewRoleDisposition.CREATED)


def revoke_grant_manual_review_role_config(
    command: RevokeGrantManualReviewRoleConfigCommand,
    transaction: Session,
) -> GrantManualReviewRoleConfigResult:
    command = _validate_revoke(command)
    transaction = _validate_transaction(transaction)
    _gate(transaction, command.published_at)
    with transaction.no_autoflush:
        _user_exists(transaction, command.confirmed_by)
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantManualReviewRoleConfig).where(
                        GrantManualReviewRoleConfig.idempotency_key == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            if replay.config_status != "REVOKED":
                _conflict()
            _validate_predecessor_chain(transaction, replay)
            role_ids = _row_role_ids(replay)
            expected = _snapshot(
                role_ids=role_ids,
                config_version=command.config_version,
                config_status="REVOKED",
                effective_from=command.effective_from,
                effective_to=None,
                confirmed_by=command.confirmed_by,
                published_at=command.published_at,
                expected_current_config_id=command.expected_current_config_id,
            )
            return _replay(replay, expected)
        current = _current(transaction)
        if (
            current is None
            or current.id != command.expected_current_config_id
            or current.config_status != "ACTIVE"
        ):
            _conflict()
        _validate_canonical(current)
        _validate_predecessor_chain(transaction, current)
        role_ids = _row_role_ids(current)
        snapshot = _snapshot(
            role_ids=role_ids,
            config_version=command.config_version,
            config_status="REVOKED",
            effective_from=command.effective_from,
            effective_to=None,
            confirmed_by=command.confirmed_by,
            published_at=command.published_at,
            expected_current_config_id=command.expected_current_config_id,
        )

    row = GrantManualReviewRoleConfig(
        id=str(uuid4()),
        gate_code=_GATE_CODE,
        scope_key=_SCOPE_KEY,
        official_copy_acquirer_role_id=role_ids[0],
        first_verifier_role_id=role_ids[1],
        second_verifier_role_id=role_ids[2],
        manual_review_proposer_role_id=role_ids[3],
        manual_review_second_reviewer_role_id=role_ids[4],
        config_version=command.config_version,
        config_status="REVOKED",
        effective_from=command.effective_from,
        effective_to=None,
        confirmed_by=command.confirmed_by,
        published_at=command.published_at,
        supersedes_config_id=current.id,
        config_snapshot=snapshot,
        config_snapshot_hash=_hash(snapshot),
        idempotency_key=command.idempotency_key,
        current_identity_key=_CURRENT_IDENTITY,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            result = transaction.execute(
                update(GrantManualReviewRoleConfig)
                .where(
                    GrantManualReviewRoleConfig.id == command.expected_current_config_id,
                    GrantManualReviewRoleConfig.config_status == "ACTIVE",
                    GrantManualReviewRoleConfig.current_identity_key == _CURRENT_IDENTITY,
                )
                .values(current_identity_key=None)
            )
            if result.rowcount != 1:
                _conflict()
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantManualReviewRoleConfig).where(
                            GrantManualReviewRoleConfig.idempotency_key
                            == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                return _replay(replay, snapshot)
        _conflict()
    return _result(row, GrantManualReviewRoleDisposition.CREATED)


def resolve_grant_manual_review_role_config(
    command: ResolveGrantManualReviewRoleConfigCommand,
    transaction: Session,
) -> GrantManualReviewRoleResolution:
    command = _validate_resolve(command)
    transaction = _validate_transaction(transaction)
    gate = _gate(transaction, command.as_of)
    with transaction.no_autoflush:
        current = _current(transaction)
        if current is None:
            _conflict()
        _validate_canonical(current)
        if (
            current.current_identity_key != _CURRENT_IDENTITY
            or current.config_status != "ACTIVE"
            or not _applicable(current.effective_from, current.effective_to, command.as_of)
        ):
            _conflict()
        _validate_predecessor_chain(transaction, current)
        role_ids = _row_role_ids(current)
        _validate_personnel_ready(transaction, role_ids)
    return GrantManualReviewRoleResolution(
        gate_id=gate.gate_id,
        config_id=current.id,
        config_snapshot_hash=current.config_snapshot_hash,
        official_copy_acquirer_role_id=role_ids[0],
        first_verifier_role_id=role_ids[1],
        second_verifier_role_id=role_ids[2],
        manual_review_proposer_role_id=role_ids[3],
        manual_review_second_reviewer_role_id=role_ids[4],
        effective_from=current.effective_from,
        effective_to=current.effective_to,
    )
