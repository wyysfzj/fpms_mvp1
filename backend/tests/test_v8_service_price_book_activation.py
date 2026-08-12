from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256
from types import ModuleType

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.errors import BusinessError
from app.db.base import Base
from app.modules.auth.models import T_User
from app.modules.fees.models import ServicePriceBook
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateStatus,
    RecordDecisionGateCommand,
    record_decision_gate,
)
from app.modules.system.models import CustomerDecisionGate

NOW = datetime(2026, 8, 13, 9, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000226"
CREATOR_ID = "00000000-0000-4000-8000-000000000224"


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
    def foreign_keys(connection, _record) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

    tables = [T_User.__table__, CustomerDecisionGate.__table__, ServicePriceBook.__table__]
    Base.metadata.create_all(engine, tables=tables)
    with engine.begin() as connection:
        for user_id, name in ((ACTOR_ID, "approver"), (CREATOR_ID, "creator")):
            connection.execute(
                T_User.__table__.insert(),
                {"id": user_id, "username": name, "password_hash": "test-only"},
            )
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _snapshot() -> str:
    return json.dumps(
        {
            "currency": "CNY",
            "discount_policy": "NONE",
            "items": [{"item_code": "FILING", "unit_price": "5000.00"}],
            "scope_key": "GLOBAL",
            "tax_policy": "EXCLUSIVE",
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _draft(transaction: Session, **changes) -> ServicePriceBook:
    snapshot = _snapshot()
    values = {
        "source_classification": "PRODUCTION",
        "book_version": "2026.08",
        "scope_key": "GLOBAL",
        "currency": "CNY",
        "tax_policy": "EXCLUSIVE",
        "discount_policy": "NONE",
        "source_reference": "managed://service-price-books/2026-08.json",
        "source_content_hash": "a" * 64,
        "item_snapshot": snapshot,
        "item_snapshot_hash": sha256(snapshot.encode()).hexdigest(),
        "item_count": 1,
        "status": "DRAFT",
        "effective_from": NOW,
        "effective_to": NOW + timedelta(days=365),
        "idempotency_key": "import-2026-08",
        "created_by": CREATOR_ID,
        "updated_by": CREATOR_ID,
    }
    values.update(changes)
    row = ServicePriceBook(**values)
    transaction.add(row)
    transaction.flush()
    return row


def _decision_value(row: ServicePriceBook) -> str:
    return json.dumps(
        {
            "book_version": row.book_version,
            "currency": row.currency,
            "discount_policy": row.discount_policy,
            "effective_from": row.effective_from.isoformat(timespec="microseconds"),
            "effective_to": row.effective_to.isoformat(timespec="microseconds"),
            "item_count": row.item_count,
            "item_snapshot_hash": row.item_snapshot_hash,
            "scope_key": row.scope_key,
            "source_content_hash": row.source_content_hash,
            "source_reference": row.source_reference,
            "tax_policy": row.tax_policy,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _gate(transaction: Session, row: ServicePriceBook) -> None:
    record_decision_gate(
        RecordDecisionGateCommand(
            gate_code=DecisionGateCode.SERVICE_RATE_VERSION,
            scope_key="GLOBAL",
            decision_value=_decision_value(row),
            decision_status=DecisionGateStatus.CONFIRMED,
            source_reference=row.source_reference,
            source_version=row.book_version,
            confirmed_by=ACTOR_ID,
            effective_at=NOW,
            idempotency_key="gate-2026-08",
            expected_current_gate_id=None,
        ),
        transaction,
    )


def _command(service: ModuleType, row: ServicePriceBook, **changes):
    command = service.ActivateServicePriceBookCommand(
        price_book_id=row.id,
        approval_reason="客户完整价格版本已独立复核",
        actor_id=ACTOR_ID,
        at=NOW,
        expected_current_price_book_id=None,
        runtime_profile="production",
    )
    return replace(command, **changes)


def _error(operation) -> BusinessError:
    with pytest.raises(BusinessError) as captured:
        operation()
    assert captured.value.code == "SERVICE_PRICE_BOOK_ACTIVATION_CONFLICT"
    assert captured.value.status_code == 409
    return captured.value


def test_activate_valid_gate_and_exact_replay(service: ModuleType, transaction: Session) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    command = _command(service, row)
    activated = service.activate_service_price_book(transaction, command)
    replay = service.activate_service_price_book(transaction, command)
    assert activated.disposition == "ACTIVATED"
    assert replay.disposition == "REUSED"
    assert activated.status == "ACTIVE"
    assert activated.current_identity_key == "GLOBAL"
    assert activated.approved_by == activated.activated_by == ACTOR_ID
    _error(
        lambda: service.activate_service_price_book(
            transaction,
            replace(command, expected_current_price_book_id=row.id),
        )
    )


def test_replay_requires_active_independent_actor(
    service: ModuleType, transaction: Session
) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    command = _command(service, row)
    service.activate_service_price_book(transaction, command)
    actor = transaction.get(T_User, ACTOR_ID)
    actor.is_active = False
    transaction.flush()
    _error(lambda: service.activate_service_price_book(transaction, command))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: setattr(row, "item_snapshot", "{}"),
        lambda row: setattr(row, "item_count", 0),
        lambda row: setattr(row, "source_classification", "TEST_ONLY"),
        lambda row: setattr(
            row,
            "item_snapshot",
            row.item_snapshot.replace('"5000.00"', '"NaN"'),
        ),
        lambda row: setattr(
            row,
            "item_snapshot",
            row.item_snapshot.replace('"item_code":"FILING"', '"item_code":" FILING"'),
        ),
    ],
)
def test_malformed_or_test_only_candidate_is_409_without_mutation(
    service: ModuleType,
    transaction: Session,
    mutation,
) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    mutation(row)
    transaction.flush()
    _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    assert row.status == "DRAFT"
    assert row.approved_by is None and row.current_identity_key is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("book_version", " 2026.08"),
        ("book_version", "2026.08\x00"),
        ("source_reference", " managed://service-price-books/2026-08.json"),
        ("source_reference", "managed://service-price-books/2026-08.json\x00"),
    ],
)
def test_persisted_activation_headers_are_canonical(
    service: ModuleType,
    transaction: Session,
    field: str,
    value: str,
) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    setattr(row, field, value)
    gate = transaction.scalar(select(CustomerDecisionGate))
    assert gate is not None
    gate.source_version = row.book_version
    gate.source_reference = row.source_reference
    gate.decision_value = _decision_value(row)
    transaction.flush()
    _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    assert row.status == "DRAFT"
    assert row.approved_by is None and row.current_identity_key is None


def test_missing_or_mismatched_gate_is_409(service: ModuleType, transaction: Session) -> None:
    row = _draft(transaction)
    _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    _gate(transaction, row)
    gate = transaction.scalar(select(CustomerDecisionGate))
    gate.decision_value = "{}"
    transaction.flush()
    _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    assert row.status == "DRAFT"


def test_test_runtime_and_same_creator_are_409(service: ModuleType, transaction: Session) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    _error(
        lambda: service.activate_service_price_book(
            transaction,
            _command(service, row, runtime_profile="test"),
        )
    )
    _error(
        lambda: service.activate_service_price_book(
            transaction,
            _command(service, row, actor_id=CREATOR_ID),
        )
    )
    assert row.status == "DRAFT"


def test_non_overlapping_predecessor_is_atomically_replaced(
    service: ModuleType,
    transaction: Session,
) -> None:
    predecessor = _draft(
        transaction,
        book_version="2025.08",
        idempotency_key="import-2025-08",
        effective_from=NOW - timedelta(days=365),
        effective_to=NOW,
    )
    predecessor.status = "ACTIVE"
    predecessor.approved_by = ACTOR_ID
    predecessor.approved_at = NOW - timedelta(days=365)
    predecessor.approval_reason = "approved"
    predecessor.activated_by = ACTOR_ID
    predecessor.activated_at = NOW - timedelta(days=365)
    predecessor.current_identity_key = "GLOBAL"
    row = _draft(transaction)
    _gate(transaction, row)
    result = service.activate_service_price_book(
        transaction,
        _command(service, row, expected_current_price_book_id=predecessor.id),
    )
    assert result.supersedes_price_book_id == predecessor.id
    assert predecessor.status == "RETIRED"
    assert predecessor.current_identity_key is None
    assert predecessor.retired_by == ACTOR_ID and predecessor.retired_at == NOW
    assert predecessor.retirement_reason == f"由服务价格版本 {row.id} 替代"


def test_replay_revalidates_exact_predecessor_retirement_tuple(
    service: ModuleType,
    transaction: Session,
) -> None:
    predecessor = _draft(
        transaction,
        book_version="2025.08",
        idempotency_key="import-2025-08",
        effective_from=NOW - timedelta(days=365),
        effective_to=NOW,
    )
    predecessor.status = "ACTIVE"
    predecessor.approved_by = ACTOR_ID
    predecessor.approved_at = NOW - timedelta(days=365)
    predecessor.approval_reason = "approved"
    predecessor.activated_by = ACTOR_ID
    predecessor.activated_at = NOW - timedelta(days=365)
    predecessor.current_identity_key = "GLOBAL"
    row = _draft(transaction)
    _gate(transaction, row)
    command = _command(service, row, expected_current_price_book_id=predecessor.id)

    service.activate_service_price_book(transaction, command)
    predecessor.retirement_reason = "corrupt replay lineage"
    transaction.flush()

    _error(lambda: service.activate_service_price_book(transaction, command))


def test_overlap_or_wrong_cas_is_409_without_mutation(
    service: ModuleType,
    transaction: Session,
) -> None:
    predecessor = _draft(transaction, book_version="2025.08", idempotency_key="old")
    predecessor.status = "ACTIVE"
    predecessor.approved_by = ACTOR_ID
    predecessor.approved_at = NOW - timedelta(days=1)
    predecessor.approval_reason = "approved"
    predecessor.activated_by = ACTOR_ID
    predecessor.activated_at = NOW - timedelta(days=1)
    predecessor.current_identity_key = "GLOBAL"
    row = _draft(transaction, effective_from=NOW + timedelta(days=1))
    _gate(transaction, row)
    _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    _error(
        lambda: service.activate_service_price_book(
            transaction,
            _command(service, row, expected_current_price_book_id=predecessor.id),
        )
    )
    assert predecessor.status == "ACTIVE" and row.status == "DRAFT"


@pytest.mark.parametrize("failure", ["integrity", "locked"])
def test_activation_write_conflicts_use_activation_code(
    service: ModuleType,
    transaction: Session,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    row = _draft(transaction)
    _gate(transaction, row)

    def fail(*_args, **_kwargs) -> None:
        if failure == "integrity":
            raise IntegrityError("write", {}, Exception())
        raise OperationalError("write", {}, Exception("database is locked"))

    monkeypatch.setattr(transaction, "flush", fail)
    error = _error(lambda: service.activate_service_price_book(transaction, _command(service, row)))
    assert (
        error.details["reason"]
        == f"database_write_{'conflict' if failure == 'integrity' else 'locked'}"
    )


def test_service_never_completes_caller_transaction(
    service: ModuleType,
    transaction: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = _draft(transaction)
    _gate(transaction, row)
    monkeypatch.setattr(transaction, "commit", lambda: pytest.fail("unexpected commit"))
    monkeypatch.setattr(transaction, "rollback", lambda: pytest.fail("unexpected rollback"))
    assert (
        service.activate_service_price_book(transaction, _command(service, row)).status == "ACTIVE"
    )
