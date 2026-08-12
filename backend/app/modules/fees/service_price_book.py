from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from typing import Literal, NoReturn

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User
from app.modules.fees.models import ServicePriceBook
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)

_HASH_HEX = frozenset("0123456789abcdef")
_SOURCE_CLASSIFICATIONS = {"PRODUCTION", "TEST_ONLY"}


@dataclass(frozen=True, slots=True, kw_only=True)
class ServicePriceBookItemInput:
    item_code: str
    unit_price: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportServicePriceBookCommand:
    source_classification: str
    book_version: str
    scope_key: str
    currency: str
    tax_policy: str
    discount_policy: str
    source_reference: str
    source_content: str
    expected_source_content_hash: str
    items: tuple[ServicePriceBookItemInput, ...]
    effective_from: datetime
    effective_to: datetime | None
    actor_id: str
    idempotency_key: str
    runtime_profile: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportServicePriceBookResult:
    price_book_id: str
    source_classification: str
    book_version: str
    scope_key: str
    currency: str
    tax_policy: str
    discount_policy: str
    source_reference: str
    source_content_hash: str
    item_snapshot_hash: str
    item_count: int
    status: str
    effective_from: datetime
    effective_to: datetime | None
    created_by: str
    disposition: Literal["CREATED", "REUSED"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivateServicePriceBookCommand:
    price_book_id: str
    approval_reason: str
    actor_id: str
    at: datetime
    expected_current_price_book_id: str | None
    runtime_profile: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivateServicePriceBookResult:
    price_book_id: str
    source_classification: str
    book_version: str
    scope_key: str
    source_content_hash: str
    item_snapshot_hash: str
    item_count: int
    status: str
    effective_from: datetime
    effective_to: datetime | None
    approved_by: str
    approved_at: datetime
    activated_by: str
    activated_at: datetime
    current_identity_key: str
    supersedes_price_book_id: str | None
    disposition: Literal["ACTIVATED", "REUSED"]


def _invalid(field: str) -> NoReturn:
    raise_business_error(
        "SERVICE_PRICE_BOOK_IMPORT_INVALID",
        "Invalid service price book import command",
        details={"field": field},
        status_code=400,
    )


def _conflict(reason: str, **details: object) -> NoReturn:
    raise_business_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        "Service price book import conflict",
        details={"reason": reason, **details},
        status_code=409,
    )


def _activation_conflict(reason: str, **details: object) -> NoReturn:
    raise_business_error(
        "SERVICE_PRICE_BOOK_ACTIVATION_CONFLICT",
        "Service price book activation conflict",
        details={"reason": reason, **details},
        status_code=409,
    )


def _activation_text(value: object, field: str, limit: int | None = None) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or (limit is not None and len(value) > limit)
    ):
        _activation_conflict("command_invalid", field=field)
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        _activation_conflict("command_invalid", field=field)
    return value


def _activation_datetime(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.utcoffset() is not None:
        _activation_conflict("command_invalid", field=field)
    return value


def _text(value: object, field: str, limit: int | None = None) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or (limit is not None and len(value) > limit)
    ):
        _invalid(field)
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
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


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _fixed_two_decimal_places(value: Decimal) -> str:
    integer, separator, fraction = format(value, "f").partition(".")
    return f"{integer}.{fraction.ljust(2, '0')}" if separator else f"{integer}.00"


def _item_snapshot(
    items: object,
    *,
    currency: str,
    tax_policy: str,
    discount_policy: str,
    scope_key: str,
) -> tuple[str, str, int]:
    if type(items) is not tuple or not items:
        _invalid("items")
    canonical_items: list[dict[str, str]] = []
    item_codes: set[str] = set()
    for item in items:
        if type(item) is not ServicePriceBookItemInput:
            _invalid("items")
        item_code = _text(item.item_code, "items.item_code", 128)
        if item_code in item_codes:
            _invalid("items.item_code")
        item_codes.add(item_code)
        unit_price = item.unit_price
        if (
            type(unit_price) is not Decimal
            or not unit_price.is_finite()
            or unit_price <= 0
            or unit_price.as_tuple().exponent < -2
        ):
            _invalid("items.unit_price")
        canonical_items.append(
            {
                "item_code": item_code,
                "unit_price": _fixed_two_decimal_places(unit_price),
            }
        )
    canonical_items.sort(key=lambda item: item["item_code"])
    snapshot = _canonical_json(
        {
            "currency": currency,
            "discount_policy": discount_policy,
            "items": canonical_items,
            "scope_key": scope_key,
            "tax_policy": tax_policy,
        }
    )
    return snapshot, sha256(snapshot.encode("utf-8")).hexdigest(), len(canonical_items)


def _result(
    row: ServicePriceBook,
    disposition: Literal["CREATED", "REUSED"],
) -> ImportServicePriceBookResult:
    return ImportServicePriceBookResult(
        price_book_id=row.id,
        source_classification=row.source_classification,
        book_version=row.book_version,
        scope_key=row.scope_key,
        currency=row.currency,
        tax_policy=row.tax_policy,
        discount_policy=row.discount_policy,
        source_reference=row.source_reference,
        source_content_hash=row.source_content_hash,
        item_snapshot_hash=row.item_snapshot_hash,
        item_count=row.item_count,
        status=row.status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        created_by=row.created_by,
        disposition=disposition,
    )


def _flush(transaction: Session, row: ServicePriceBook) -> None:
    try:
        transaction.flush([row])
    except IntegrityError:
        _conflict("database_write_conflict")
    except OperationalError as exc:
        if "database is locked" in str(exc.orig).lower():
            _conflict("database_write_locked")
        raise


def _activation_flush(transaction: Session, *rows: ServicePriceBook) -> None:
    try:
        transaction.flush(list(rows) or None)
    except IntegrityError:
        _activation_conflict("database_write_conflict")
    except OperationalError as exc:
        if "database is locked" in str(exc.orig).lower():
            _activation_conflict("database_write_locked")
        raise


def import_service_price_book(
    transaction: Session,
    command: ImportServicePriceBookCommand,
) -> ImportServicePriceBookResult:
    if type(command) is not ImportServicePriceBookCommand:
        _invalid("command")
    source_classification = _text(
        command.source_classification,
        "source_classification",
        24,
    )
    if source_classification not in _SOURCE_CLASSIFICATIONS:
        _invalid("source_classification")
    book_version = _text(command.book_version, "book_version", 128)
    scope_key = _text(command.scope_key, "scope_key", 128)
    if scope_key != "GLOBAL":
        _invalid("scope_key")
    currency = _text(command.currency, "currency", 8)
    if (
        len(currency) != 3
        or not currency.isascii()
        or not currency.isalpha()
        or not currency.isupper()
    ):
        _invalid("currency")
    tax_policy = _text(command.tax_policy, "tax_policy")
    discount_policy = _text(command.discount_policy, "discount_policy")
    source_reference = _text(command.source_reference, "source_reference")
    source_content = _text(command.source_content, "source_content")
    expected_source_hash = _hash_text(
        command.expected_source_content_hash,
        "expected_source_content_hash",
    )
    effective_from = _naive_datetime(command.effective_from, "effective_from")
    if command.effective_to is None:
        effective_to = None
    else:
        effective_to = _naive_datetime(command.effective_to, "effective_to")
        if effective_to <= effective_from:
            _invalid("effective_to")
    actor_id = _text(command.actor_id, "actor_id", 36)
    idempotency_key = _text(command.idempotency_key, "idempotency_key", 128)
    runtime_profile = _text(command.runtime_profile, "runtime_profile", 64)
    if source_classification == "TEST_ONLY" and runtime_profile != "test":
        _conflict("test_only_import_outside_test_profile")

    source_snapshot = _canonical_json(
        {
            "source_content": source_content,
            "source_reference": source_reference,
        }
    )
    source_hash = sha256(source_snapshot.encode("utf-8")).hexdigest()
    if source_hash != expected_source_hash:
        _conflict("source_content_hash_mismatch")
    item_snapshot, item_snapshot_hash, item_count = _item_snapshot(
        command.items,
        currency=currency,
        tax_policy=tax_policy,
        discount_policy=discount_policy,
        scope_key=scope_key,
    )

    with transaction.no_autoflush:
        existing = transaction.scalar(
            select(ServicePriceBook).where(ServicePriceBook.idempotency_key == idempotency_key)
        )
    expected = (
        source_classification,
        book_version,
        scope_key,
        currency,
        tax_policy,
        discount_policy,
        source_reference,
        source_hash,
        item_snapshot,
        item_snapshot_hash,
        item_count,
        effective_from,
        effective_to,
        actor_id,
    )
    if existing is not None:
        stored_snapshot_hash = sha256(existing.item_snapshot.encode("utf-8")).hexdigest()
        actual = (
            existing.source_classification,
            existing.book_version,
            existing.scope_key,
            existing.currency,
            existing.tax_policy,
            existing.discount_policy,
            existing.source_reference,
            existing.source_content_hash,
            existing.item_snapshot,
            existing.item_snapshot_hash,
            existing.item_count,
            existing.effective_from,
            existing.effective_to,
            existing.created_by,
        )
        untouched_draft = (
            existing.status == "DRAFT"
            and existing.approved_by is None
            and existing.approved_at is None
            and existing.approval_reason is None
            and existing.activated_by is None
            and existing.activated_at is None
            and existing.retired_by is None
            and existing.retired_at is None
            and existing.retirement_reason is None
            and existing.supersedes_price_book_id is None
            and existing.current_identity_key is None
        )
        if (
            actual != expected
            or stored_snapshot_hash != existing.item_snapshot_hash
            or not untouched_draft
        ):
            _conflict("idempotency_replay_conflict", price_book_id=existing.id)
        return _result(existing, "REUSED")

    with transaction.no_autoflush:
        version_conflict = transaction.scalar(
            select(ServicePriceBook.id).where(
                ServicePriceBook.scope_key == scope_key,
                ServicePriceBook.book_version == book_version,
            )
        )
    if version_conflict is not None:
        _conflict("book_version_conflict", price_book_id=version_conflict)

    row = ServicePriceBook(
        source_classification=source_classification,
        book_version=book_version,
        scope_key=scope_key,
        currency=currency,
        tax_policy=tax_policy,
        discount_policy=discount_policy,
        source_reference=source_reference,
        source_content_hash=source_hash,
        item_snapshot=item_snapshot,
        item_snapshot_hash=item_snapshot_hash,
        item_count=item_count,
        status="DRAFT",
        effective_from=effective_from,
        effective_to=effective_to,
        idempotency_key=idempotency_key,
        created_by=actor_id,
        updated_by=actor_id,
    )
    transaction.add(row)
    _flush(transaction, row)
    return _result(row, "CREATED")


def _activation_result(
    row: ServicePriceBook,
    disposition: Literal["ACTIVATED", "REUSED"],
) -> ActivateServicePriceBookResult:
    if (
        row.approved_by is None
        or row.approved_at is None
        or row.activated_by is None
        or row.activated_at is None
        or row.current_identity_key is None
    ):
        _activation_conflict("persisted_activation_tuple_invalid", price_book_id=row.id)
    return ActivateServicePriceBookResult(
        price_book_id=row.id,
        source_classification=row.source_classification,
        book_version=row.book_version,
        scope_key=row.scope_key,
        source_content_hash=row.source_content_hash,
        item_snapshot_hash=row.item_snapshot_hash,
        item_count=row.item_count,
        status=row.status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        approved_by=row.approved_by,
        approved_at=row.approved_at,
        activated_by=row.activated_by,
        activated_at=row.activated_at,
        current_identity_key=row.current_identity_key,
        supersedes_price_book_id=row.supersedes_price_book_id,
        disposition=disposition,
    )


def _activation_snapshot(row: ServicePriceBook) -> str:
    if (
        type(row.book_version) is not str
        or not row.book_version
        or type(row.scope_key) is not str
        or type(row.currency) is not str
        or len(row.currency) != 3
        or not row.currency.isascii()
        or not row.currency.isalpha()
        or not row.currency.isupper()
        or type(row.tax_policy) is not str
        or not row.tax_policy
        or row.tax_policy != row.tax_policy.strip()
        or type(row.discount_policy) is not str
        or not row.discount_policy
        or row.discount_policy != row.discount_policy.strip()
        or type(row.source_reference) is not str
        or not row.source_reference
        or type(row.source_content_hash) is not str
        or type(row.item_snapshot) is not str
        or type(row.item_snapshot_hash) is not str
        or type(row.item_count) is not int
        or type(row.effective_from) is not datetime
        or row.effective_from.utcoffset() is not None
        or (
            row.effective_to is not None
            and (type(row.effective_to) is not datetime or row.effective_to.utcoffset() is not None)
        )
        or (row.effective_to is not None and row.effective_to <= row.effective_from)
    ):
        _activation_conflict("persisted_candidate_invalid", price_book_id=row.id)
    try:
        parsed = json.loads(row.item_snapshot)
        canonical = _canonical_json(parsed)
    except (TypeError, ValueError, UnicodeEncodeError):
        _activation_conflict("item_snapshot_invalid", price_book_id=row.id)
    expected_keys = {
        "currency",
        "discount_policy",
        "items",
        "scope_key",
        "tax_policy",
    }
    items = parsed.get("items") if type(parsed) is dict else None
    valid_items = type(items) is list and len(items) == row.item_count and row.item_count > 0
    previous_code: str | None = None
    if valid_items:
        for item in items:
            if type(item) is not dict or set(item) != {"item_code", "unit_price"}:
                valid_items = False
                break
            code = item["item_code"]
            price_text = item["unit_price"]
            if (
                type(code) is not str
                or not code
                or code != code.strip()
                or "\x00" in code
                or len(code) > 128
                or (previous_code is not None and code <= previous_code)
                or type(price_text) is not str
            ):
                valid_items = False
                break
            try:
                price = Decimal(price_text)
            except Exception:
                valid_items = False
                break
            if (
                not price.is_finite()
                or price <= 0
                or price.as_tuple().exponent != -2
                or _fixed_two_decimal_places(price) != price_text
            ):
                valid_items = False
                break
            previous_code = code
    if (
        type(parsed) is not dict
        or set(parsed) != expected_keys
        or canonical != row.item_snapshot
        or parsed["currency"] != row.currency
        or parsed["discount_policy"] != row.discount_policy
        or parsed["scope_key"] != row.scope_key
        or parsed["tax_policy"] != row.tax_policy
        or not valid_items
        or sha256(canonical.encode("utf-8")).hexdigest() != row.item_snapshot_hash
        or len(row.source_content_hash) != 64
        or any(character not in _HASH_HEX for character in row.source_content_hash)
        or len(row.item_snapshot_hash) != 64
        or any(character not in _HASH_HEX for character in row.item_snapshot_hash)
    ):
        _activation_conflict("item_snapshot_invalid", price_book_id=row.id)
    return _canonical_json(
        {
            "book_version": row.book_version,
            "currency": row.currency,
            "discount_policy": row.discount_policy,
            "effective_from": row.effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                None
                if row.effective_to is None
                else row.effective_to.isoformat(timespec="microseconds")
            ),
            "item_count": row.item_count,
            "item_snapshot_hash": row.item_snapshot_hash,
            "scope_key": row.scope_key,
            "source_content_hash": row.source_content_hash,
            "source_reference": row.source_reference,
            "tax_policy": row.tax_policy,
        }
    )


def activate_service_price_book(
    transaction: Session,
    command: ActivateServicePriceBookCommand,
) -> ActivateServicePriceBookResult:
    if type(command) is not ActivateServicePriceBookCommand:
        _activation_conflict("command_invalid")
    price_book_id = _activation_text(command.price_book_id, "price_book_id", 36)
    approval_reason = _activation_text(command.approval_reason, "approval_reason")
    actor_id = _activation_text(command.actor_id, "actor_id", 36)
    at = _activation_datetime(command.at, "at")
    runtime_profile = _activation_text(command.runtime_profile, "runtime_profile", 64)
    expected_current = command.expected_current_price_book_id
    if expected_current is not None:
        expected_current = _activation_text(
            expected_current,
            "expected_current_price_book_id",
            36,
        )
    with transaction.no_autoflush:
        row = transaction.get(ServicePriceBook, price_book_id)
    if row is None:
        _activation_conflict("price_book_not_found", price_book_id=price_book_id)
    decision_value = _activation_snapshot(row)
    if (
        row.source_classification != "PRODUCTION"
        or runtime_profile == "test"
        or row.scope_key != "GLOBAL"
        or row.effective_from > at
        or (row.effective_to is not None and at >= row.effective_to)
    ):
        _activation_conflict("candidate_not_eligible", price_book_id=row.id)
    try:
        gate = resolve_decision_gate(
            ResolveDecisionGateCommand(
                gate_code=DecisionGateCode.SERVICE_RATE_VERSION,
                scope_key="GLOBAL",
                as_of=at,
            ),
            transaction,
        )
    except BusinessError:
        _activation_conflict("decision_gate_unavailable")
    if (
        gate.resolved_scope_key != "GLOBAL"
        or gate.source_reference != row.source_reference
        or gate.source_version != row.book_version
        or gate.decision_value != decision_value
    ):
        _activation_conflict("decision_gate_mismatch", price_book_id=row.id)
    if (
        row.status == "ACTIVE"
        and row.current_identity_key == "GLOBAL"
        and row.approved_by == actor_id
        and row.approved_at == at
        and row.approval_reason == approval_reason
        and row.activated_by == actor_id
        and row.activated_at == at
    ):
        with transaction.no_autoflush:
            replay_actor = transaction.get(T_User, actor_id)
        if (
            replay_actor is None
            or not replay_actor.is_active
            or row.created_by == actor_id
            or expected_current != row.supersedes_price_book_id
            or row.source_classification != "PRODUCTION"
            or row.scope_key != "GLOBAL"
            or row.retired_by is not None
            or row.retired_at is not None
            or row.retirement_reason is not None
        ):
            _activation_conflict("activation_replay_conflict", price_book_id=row.id)
        return _activation_result(row, "REUSED")
    if (
        row.status != "DRAFT"
        or row.approved_by is not None
        or row.approved_at is not None
        or row.approval_reason is not None
        or row.activated_by is not None
        or row.activated_at is not None
        or row.retired_by is not None
        or row.retired_at is not None
        or row.retirement_reason is not None
        or row.supersedes_price_book_id is not None
        or row.current_identity_key is not None
        or row.created_by == actor_id
    ):
        _activation_conflict("candidate_predecessor_invalid", price_book_id=row.id)
    with transaction.no_autoflush:
        current_rows = list(
            transaction.scalars(
                select(ServicePriceBook).where(ServicePriceBook.current_identity_key == "GLOBAL")
            ).all()
        )
        actor = transaction.get(T_User, actor_id)
    if actor is None or not actor.is_active:
        _activation_conflict("actor_not_active", actor_id=actor_id)
    if len(current_rows) > 1:
        _activation_conflict("current_multiplicity", count=len(current_rows))
    predecessor = current_rows[0] if current_rows else None
    actual_current = None if predecessor is None else predecessor.id
    if expected_current != actual_current:
        _activation_conflict(
            "current_compare_and_set_conflict",
            expected=expected_current,
            actual=actual_current,
        )
    if predecessor is not None:
        if (
            predecessor.id == row.id
            or predecessor.source_classification != "PRODUCTION"
            or predecessor.scope_key != "GLOBAL"
            or predecessor.status != "ACTIVE"
            or predecessor.current_identity_key != "GLOBAL"
            or predecessor.approved_by is None
            or predecessor.approved_at is None
            or predecessor.activated_by is None
            or predecessor.activated_at is None
            or predecessor.retired_by is not None
            or predecessor.retired_at is not None
            or predecessor.retirement_reason is not None
            or predecessor.effective_to is None
            or predecessor.effective_to > row.effective_from
        ):
            _activation_conflict("current_predecessor_invalid", predecessor_id=predecessor.id)
        _activation_snapshot(predecessor)
        predecessor.status = "RETIRED"
        predecessor.retired_by = actor_id
        predecessor.retired_at = at
        predecessor.retirement_reason = f"由服务价格版本 {row.id} 替代"
        predecessor.current_identity_key = None
        predecessor.updated_by = actor_id
        predecessor.updated_at = at
        row.supersedes_price_book_id = predecessor.id
        _activation_flush(transaction, predecessor)
    row.approved_by = actor_id
    row.approved_at = at
    row.approval_reason = approval_reason
    row.activated_by = actor_id
    row.activated_at = at
    row.status = "ACTIVE"
    row.current_identity_key = "GLOBAL"
    row.updated_by = actor_id
    row.updated_at = at
    _activation_flush(transaction, row)
    return _activation_result(row, "ACTIVATED")
