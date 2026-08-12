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

from app.core.errors import raise_business_error
from app.modules.fees.models import ServicePriceBook

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
