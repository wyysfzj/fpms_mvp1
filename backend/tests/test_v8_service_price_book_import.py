from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal, localcontext
from hashlib import sha256
from types import ModuleType

import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.errors import BusinessError
from app.db.base import Base
from app.modules.auth.models import T_User
from app.modules.fees.models import ServicePriceBook

NOW = datetime(2026, 8, 13, 9, 0)
LATER = NOW + timedelta(days=365)
ACTOR_ID = "00000000-0000-4000-8000-000000000224"
SOURCE_REFERENCE = "managed://service-price-books/customer-approved-2026-08.json"
SOURCE_CONTENT = '{"version":"2026.08","controlled_upload":true}'


@pytest.fixture
def service() -> ModuleType:
    from app.modules.fees import service_price_book

    return service_price_book


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

    Base.metadata.create_all(engine, tables=[T_User.__table__, ServicePriceBook.__table__])
    with engine.begin() as connection:
        connection.execute(
            T_User.__table__.insert(),
            {
                "id": ACTOR_ID,
                "username": "service-price-book-importer",
                "password_hash": "test-only",
            },
        )
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _canonical_source_hash() -> str:
    snapshot = json.dumps(
        {
            "source_content": SOURCE_CONTENT,
            "source_reference": SOURCE_REFERENCE,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(snapshot.encode("utf-8")).hexdigest()


def _command(service: ModuleType, **changes):
    command = service.ImportServicePriceBookCommand(
        source_classification="PRODUCTION",
        book_version="2026.08",
        scope_key="GLOBAL",
        currency="CNY",
        tax_policy="EXCLUSIVE",
        discount_policy="NONE",
        source_reference=SOURCE_REFERENCE,
        source_content=SOURCE_CONTENT,
        expected_source_content_hash=_canonical_source_hash(),
        items=(
            service.ServicePriceBookItemInput(
                item_code="SEARCH|STANDARD",
                unit_price=Decimal("1200.00"),
            ),
            service.ServicePriceBookItemInput(
                item_code="FILING:STANDARD",
                unit_price=Decimal("5000.50"),
            ),
        ),
        effective_from=NOW,
        effective_to=LATER,
        actor_id=ACTOR_ID,
        idempotency_key="service-price-book-import-2026-08",
        runtime_profile="production",
    )
    return replace(command, **changes)


def _count(transaction: Session) -> int:
    return transaction.scalar(select(func.count(ServicePriceBook.id))) or 0


def _expect_error(code: str, status: int, operation) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        operation()
    assert captured.value.code == code
    assert captured.value.status_code == status
    return captured.value


def test_import_stores_delimiter_safe_snapshots_and_reuses_exact_draft(
    service: ModuleType,
    transaction: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_transaction_completion() -> None:
        raise AssertionError("service must not complete the caller-owned transaction")

    monkeypatch.setattr(transaction, "commit", forbidden_transaction_completion)
    monkeypatch.setattr(transaction, "rollback", forbidden_transaction_completion)
    command = _command(service)

    created = service.import_service_price_book(transaction, command)

    assert created.disposition == "CREATED"
    assert created.status == "DRAFT"
    assert created.item_count == 2
    assert created.source_classification == "PRODUCTION"
    assert created.source_content_hash == command.expected_source_content_hash
    row = transaction.get(ServicePriceBook, created.price_book_id)
    assert row is not None
    assert json.loads(row.item_snapshot) == {
        "currency": "CNY",
        "discount_policy": "NONE",
        "items": [
            {"item_code": "FILING:STANDARD", "unit_price": "5000.50"},
            {"item_code": "SEARCH|STANDARD", "unit_price": "1200.00"},
        ],
        "scope_key": "GLOBAL",
        "tax_policy": "EXCLUSIVE",
    }
    assert sha256(row.item_snapshot.encode("utf-8")).hexdigest() == row.item_snapshot_hash
    assert row.status == "DRAFT"
    assert row.approved_by is None
    assert row.activated_by is None
    assert row.current_identity_key is None

    replay = service.import_service_price_book(transaction, command)
    assert replay.disposition == "REUSED"
    assert replay.price_book_id == created.price_book_id
    assert _count(transaction) == 1


def test_canonical_price_scale_and_item_order_reuse_one_snapshot(
    service: ModuleType,
    transaction: Session,
) -> None:
    command = _command(
        service,
        items=(
            service.ServicePriceBookItemInput(
                item_code="SEARCH|STANDARD",
                unit_price=Decimal("1200"),
            ),
            service.ServicePriceBookItemInput(
                item_code="FILING:STANDARD",
                unit_price=Decimal("5000.5"),
            ),
        ),
    )
    created = service.import_service_price_book(transaction, command)
    replay = service.import_service_price_book(
        transaction,
        replace(
            command,
            items=(
                service.ServicePriceBookItemInput(
                    item_code="FILING:STANDARD",
                    unit_price=Decimal("5000.50"),
                ),
                service.ServicePriceBookItemInput(
                    item_code="SEARCH|STANDARD",
                    unit_price=Decimal("1200.00"),
                ),
            ),
        ),
    )
    row = transaction.get(ServicePriceBook, created.price_book_id)
    assert row is not None
    assert replay.disposition == "REUSED"
    assert replay.item_snapshot_hash == created.item_snapshot_hash == row.item_snapshot_hash
    assert '"unit_price":"1200.00"' in row.item_snapshot
    assert '"unit_price":"5000.50"' in row.item_snapshot
    assert _count(transaction) == 1


def test_canonical_price_is_independent_of_decimal_context(
    service: ModuleType,
    transaction: Session,
) -> None:
    command = _command(
        service,
        items=(
            service.ServicePriceBookItemInput(
                item_code="LARGE",
                unit_price=Decimal("1E+26"),
            ),
            service.ServicePriceBookItemInput(
                item_code="ORDINARY",
                unit_price=Decimal("5000.50"),
            ),
        ),
    )
    with localcontext() as context:
        context.prec = 4
        created = service.import_service_price_book(transaction, command)
    row = transaction.get(ServicePriceBook, created.price_book_id)
    assert row is not None
    snapshot = json.loads(row.item_snapshot)
    assert snapshot["items"] == [
        {"item_code": "LARGE", "unit_price": "100000000000000000000000000.00"},
        {"item_code": "ORDINARY", "unit_price": "5000.50"},
    ]
    assert sha256(row.item_snapshot.encode("utf-8")).hexdigest() == row.item_snapshot_hash


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"scope_key": "CASE"}, "scope_key"),
        ({"currency": "cny"}, "currency"),
        ({"tax_policy": ""}, "tax_policy"),
        ({"discount_policy": " NONE"}, "discount_policy"),
        ({"source_classification": "UNKNOWN"}, "source_classification"),
        ({"effective_to": NOW}, "effective_to"),
        ({"items": ()}, "items"),
    ],
)
def test_invalid_header_input_is_400_without_write(
    service: ModuleType,
    transaction: Session,
    changes: dict[str, object],
    field: str,
) -> None:
    error = _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_INVALID",
        400,
        lambda: service.import_service_price_book(transaction, _command(service, **changes)),
    )
    assert error.details == {"field": field}
    assert _count(transaction) == 0


@pytest.mark.parametrize(
    ("items_factory", "field"),
    [
        (
            lambda service: (
                service.ServicePriceBookItemInput(item_code="DUP", unit_price=Decimal("1.00")),
                service.ServicePriceBookItemInput(item_code="DUP", unit_price=Decimal("2.00")),
            ),
            "items.item_code",
        ),
        (
            lambda service: (service.ServicePriceBookItemInput(item_code="ITEM", unit_price=1),),
            "items.unit_price",
        ),
        (
            lambda service: (
                service.ServicePriceBookItemInput(item_code="ITEM", unit_price=Decimal("NaN")),
            ),
            "items.unit_price",
        ),
        (
            lambda service: (
                service.ServicePriceBookItemInput(item_code="ITEM", unit_price=Decimal("0.00")),
            ),
            "items.unit_price",
        ),
        (
            lambda service: (
                service.ServicePriceBookItemInput(item_code="ITEM", unit_price=Decimal("1.001")),
            ),
            "items.unit_price",
        ),
    ],
)
def test_invalid_item_input_is_400_without_write(
    service: ModuleType,
    transaction: Session,
    items_factory,
    field: str,
) -> None:
    error = _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_INVALID",
        400,
        lambda: service.import_service_price_book(
            transaction,
            _command(service, items=items_factory(service)),
        ),
    )
    assert error.details == {"field": field}
    assert _count(transaction) == 0


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"source_content": "bad\ud800text"}, "source_content"),
        ({"source_reference": "bad\ud800reference"}, "source_reference"),
        ({"tax_policy": "bad\ud800policy"}, "tax_policy"),
    ],
)
def test_non_utf8_header_text_is_400_without_write(
    service: ModuleType,
    transaction: Session,
    changes: dict[str, object],
    field: str,
) -> None:
    error = _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_INVALID",
        400,
        lambda: service.import_service_price_book(transaction, _command(service, **changes)),
    )
    assert error.details == {"field": field}
    assert _count(transaction) == 0


def test_non_utf8_item_code_is_400_without_write(
    service: ModuleType,
    transaction: Session,
) -> None:
    error = _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_INVALID",
        400,
        lambda: service.import_service_price_book(
            transaction,
            _command(
                service,
                items=(
                    service.ServicePriceBookItemInput(
                        item_code="bad\ud800item",
                        unit_price=Decimal("1.00"),
                    ),
                ),
            ),
        ),
    )
    assert error.details == {"field": "items.item_code"}
    assert _count(transaction) == 0


def test_test_only_requires_explicit_test_profile_and_retains_classification(
    service: ModuleType,
    transaction: Session,
) -> None:
    command = _command(service, source_classification="TEST_ONLY")
    _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        409,
        lambda: service.import_service_price_book(transaction, command),
    )
    assert _count(transaction) == 0

    created = service.import_service_price_book(
        transaction,
        replace(command, runtime_profile="test"),
    )
    assert created.source_classification == "TEST_ONLY"
    assert created.status == "DRAFT"


def test_source_version_and_idempotency_conflicts_are_409_without_extra_write(
    service: ModuleType,
    transaction: Session,
) -> None:
    command = _command(service)
    _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        409,
        lambda: service.import_service_price_book(
            transaction,
            replace(command, expected_source_content_hash="0" * 64),
        ),
    )
    assert _count(transaction) == 0

    created = service.import_service_price_book(transaction, command)
    _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        409,
        lambda: service.import_service_price_book(
            transaction,
            replace(command, currency="USD"),
        ),
    )
    _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        409,
        lambda: service.import_service_price_book(
            transaction,
            replace(command, idempotency_key="different-import-key"),
        ),
    )
    assert _count(transaction) == 1
    assert transaction.get(ServicePriceBook, created.price_book_id) is not None


def test_replay_rejects_tampered_snapshot(
    service: ModuleType,
    transaction: Session,
) -> None:
    command = _command(service)
    created = service.import_service_price_book(transaction, command)
    row = transaction.get(ServicePriceBook, created.price_book_id)
    assert row is not None
    row.item_snapshot = "{}"

    _expect_error(
        "SERVICE_PRICE_BOOK_IMPORT_CONFLICT",
        409,
        lambda: service.import_service_price_book(transaction, command),
    )
    assert _count(transaction) == 1
