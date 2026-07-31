from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.fees import official_rate_book
from app.modules.fees.cnipa_layout_rate_candidate import materialize_cnipa_layout_246
from app.modules.fees.models import FeeRate, OfficialRateBook

FEE_CODE = "IC_LAYOUT_REGISTRATION_FEE"
BOOK_CODE = "CNIPA_LAYOUT_246"
VERSION = "2017-07-01"
SOURCE_URL = "https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html"
SNAPSHOT_HASH = "f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4"
APPROVED_AT = datetime(2026, 7, 18, 10, 0)
ACTIVATED_AT = datetime(2026, 7, 18, 10, 1)


def _public_boundary():
    return (
        official_rate_book.GetLayoutRegistrationFeeCommand,
        official_rate_book.GetLayoutRegistrationFeeResult,
        official_rate_book.get_layout_registration_fee,
    )


def _actor(transaction: Session) -> T_User:
    actor = T_User(
        id=str(uuid4()),
        username=f"layout-rate-{uuid4()}",
        password_hash="not-used",
        is_active=True,
    )
    transaction.add(actor)
    transaction.flush()
    return actor


def _active_graph(transaction: Session) -> tuple[OfficialRateBook, FeeRate]:
    created = materialize_cnipa_layout_246(transaction)
    actor = _actor(transaction)
    official_rate_book.activate_official_rate_book(
        official_rate_book.ActivateOfficialRateBookCommand(
            rate_book_id=created.rate_book_id,
            approved_by=actor.id,
            approved_at=APPROVED_AT,
            activated_by=actor.id,
            activated_at=ACTIVATED_AT,
            expected_current_rate_book_id=None,
        ),
        transaction,
    )
    transaction.expire_all()
    book = transaction.get(OfficialRateBook, created.rate_book_id)
    rate = transaction.get(FeeRate, created.rate_id)
    assert book is not None
    assert rate is not None
    return book, rate


def _command(effective_date: object):
    command_type, _, _ = _public_boundary()
    return command_type(effective_date=effective_date)


def _read(transaction: Session, effective_date: object = date(2017, 7, 1)):
    _, _, get_layout_registration_fee = _public_boundary()
    return get_layout_registration_fee(_command(effective_date), transaction)


def _assert_error(status_code: int, callable_) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        callable_()
    assert caught.value.status_code == status_code
    return caught.value


def test_layout_registration_fee_rule_exposes_exact_public_boundary() -> None:
    expected = (
        "GetLayoutRegistrationFeeCommand",
        "GetLayoutRegistrationFeeResult",
        "get_layout_registration_fee",
    )
    missing = tuple(
        name
        for name in expected
        if name not in official_rate_book.__all__ or not hasattr(official_rate_book, name)
    )
    assert missing == ()

    command_type, result_type, _ = _public_boundary()
    assert tuple(field.name for field in fields(command_type)) == ("effective_date",)
    assert tuple(field.name for field in fields(result_type)) == (
        "rate_id",
        "fee_code",
        "fee_type",
        "currency",
        "calc_mode",
        "allow_reduction",
        "enabled",
        "amount",
        "rate_book_id",
        "book_code",
        "version_code",
        "effective_from",
        "effective_to",
        "approval_status",
        "activation_status",
        "source_reference",
        "source_version",
        "source_snapshot_hash",
    )


@pytest.mark.parametrize("effective_date", [date(2017, 7, 1), date(2035, 12, 31)])
def test_returns_exact_persisted_amount_rate_book_and_source_values(
    session_factory: sessionmaker,
    effective_date: date,
) -> None:
    with session_factory() as transaction:
        book, rate = _active_graph(transaction)

        result = _read(transaction, effective_date)

        assert result.rate_id == rate.id
        assert result.fee_code == FEE_CODE
        assert result.fee_type == "GOV"
        assert result.currency == "CNY"
        assert result.calc_mode == "FIXED"
        assert result.allow_reduction is False
        assert result.enabled is True
        assert result.amount == Decimal("1000.00")
        assert result.rate_book_id == book.id
        assert result.book_code == BOOK_CODE
        assert result.version_code == VERSION
        assert result.effective_from == date(2017, 7, 1)
        assert result.effective_to is None
        assert result.approval_status == "APPROVED"
        assert result.activation_status == "ACTIVE"
        assert result.source_reference == SOURCE_URL
        assert result.source_version == VERSION
        assert result.source_snapshot_hash == SNAPSHOT_HASH


@pytest.mark.parametrize(
    "command",
    [
        object(),
        None,
    ],
)
def test_rejects_wrong_command_type_before_selection(
    session_factory: sessionmaker,
    command: object,
) -> None:
    with session_factory() as transaction:
        _, _, get_layout_registration_fee = _public_boundary()
        error = _assert_error(
            400,
            lambda: get_layout_registration_fee(command, transaction),
        )
        assert error.details == {"field": "command"}


@pytest.mark.parametrize(
    "effective_date",
    [
        None,
        "2017-07-01",
        datetime(2017, 7, 1),
        date(2017, 6, 30),
    ],
)
def test_rejects_invalid_or_unsupported_effective_date_before_selection(
    session_factory: sessionmaker,
    effective_date: object,
) -> None:
    with session_factory() as transaction:
        error = _assert_error(400, lambda: _read(transaction, effective_date))
        assert error.details == {"field": "effective_date"}


def test_missing_or_inactive_candidate_is_409_without_fallback(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        legacy = FeeRate(
            fee_code=FEE_CODE,
            fee_type="GOV",
            currency="CNY",
            default_amount=Decimal("1000.00"),
            calc_mode="FIXED",
            allow_reduction=False,
            enabled=True,
            source_status="CONFIRMED",
            source_url="http://www.tianyueip.com/product/612",
            official_rate_book_id=None,
        )
        transaction.add(legacy)
        transaction.flush()

        error = _assert_error(409, lambda: _read(transaction))
        assert error.details == {"field": "rate_book"}

        materialize_cnipa_layout_246(transaction)
        error = _assert_error(409, lambda: _read(transaction))
        assert error.details == {"field": "rate_book"}


@pytest.mark.parametrize(
    ("table", "assignment", "value", "field"),
    [
        ("t_fee_rate_book", "source_snapshot_hash", "0" * 64, "source_snapshot_hash"),
        ("t_fee_rate_book", "source_version", "changed", "source_version"),
        ("t_fee_rate", "enabled", False, "enabled"),
        ("t_fee_rate", "source_status", "CONFIRMED", "source_status"),
        ("t_fee_rate", "source_url", "https://www.cnipa.gov.cn/changed", "source_url"),
        ("t_fee_rate", "default_amount", "999.00", "default_amount"),
        ("t_fee_rate", "effective_from", "2017-07-02", "effective_from"),
        ("t_fee_rate", "official_rate_book_id", None, "rate"),
    ],
)
def test_changed_book_rate_or_source_fails_closed_without_repair(
    session_factory: sessionmaker,
    table: str,
    assignment: str,
    value: object,
    field: str,
) -> None:
    with session_factory() as transaction:
        book, rate = _active_graph(transaction)
        row_id = book.id if table == "t_fee_rate_book" else rate.id
        transaction.execute(
            text(f"UPDATE {table} SET {assignment} = :value WHERE id = :row_id"),
            {"value": value, "row_id": row_id},
        )
        transaction.expire_all()

        error = _assert_error(409, lambda: _read(transaction))
        assert error.details == {"field": field}
        persisted = transaction.scalar(
            text(f"SELECT {assignment} FROM {table} WHERE id = :row_id"),
            {"row_id": row_id},
        )
        if assignment == "default_amount":
            assert Decimal(str(persisted)) == Decimal(str(value))
        else:
            assert persisted == value


@pytest.mark.parametrize(
    ("table", "assignment", "value", "field"),
    [
        ("t_fee_rate_book", "source_published_on", "not-a-date", "source_published_on"),
        ("t_fee_rate", "effective_from", "not-a-date", "effective_from"),
        ("t_fee_rate", "default_amount", "not-a-decimal", "default_amount"),
    ],
)
def test_malformed_raw_persisted_values_are_409(
    session_factory: sessionmaker,
    table: str,
    assignment: str,
    value: str,
    field: str,
) -> None:
    with session_factory() as transaction:
        book, rate = _active_graph(transaction)
        row_id = book.id if table == "t_fee_rate_book" else rate.id
        transaction.execute(
            text(f"UPDATE {table} SET {assignment} = :value WHERE id = :row_id"),
            {"value": value, "row_id": row_id},
        )
        transaction.expire_all()

        error = _assert_error(409, lambda: _read(transaction))

        assert error.details == {"field": field}


@pytest.mark.parametrize("assignment", ["enabled", "allow_reduction"])
def test_non_boolean_raw_storage_is_409(
    session_factory: sessionmaker,
    assignment: str,
) -> None:
    with session_factory() as transaction:
        _, rate = _active_graph(transaction)
        transaction.execute(
            text(f"UPDATE t_fee_rate SET {assignment} = 2 WHERE id = :rate_id"),
            {"rate_id": rate.id},
        )
        transaction.expire_all()

        error = _assert_error(409, lambda: _read(transaction))

        assert error.details == {"field": assignment}
        assert (
            transaction.scalar(
                text(f"SELECT {assignment} FROM t_fee_rate WHERE id = :rate_id"),
                {"rate_id": rate.id},
            )
            == 2
        )


def test_rejects_activation_chronology_contradiction(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        book, _ = _active_graph(transaction)
        transaction.execute(
            text("UPDATE t_fee_rate_book SET approved_at = :approved_at WHERE id = :rate_book_id"),
            {
                "approved_at": datetime(2026, 7, 18, 10, 2),
                "rate_book_id": book.id,
            },
        )
        transaction.expire_all()

        error = _assert_error(409, lambda: _read(transaction))

        assert error.details == {"field": "approved_at/activated_at"}


def test_rejects_non_two_place_raw_amount_even_when_orm_rounds_it(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, rate = _active_graph(transaction)
        transaction.execute(
            text("UPDATE t_fee_rate SET default_amount = 1000.001 WHERE id = :rate_id"),
            {"rate_id": rate.id},
        )
        transaction.expire_all()

        error = _assert_error(409, lambda: _read(transaction))

        assert error.details == {"field": "default_amount"}
        assert (
            transaction.scalar(
                text("SELECT CAST(default_amount AS TEXT) FROM t_fee_rate WHERE id = :rate_id"),
                {"rate_id": rate.id},
            )
            == "1000.001"
        )


def test_missing_or_multiple_linked_rate_is_409(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        book, rate = _active_graph(transaction)
        transaction.delete(rate)
        transaction.flush()
        error = _assert_error(409, lambda: _read(transaction))
        assert error.details == {"field": "rate"}

    with session_factory() as transaction:
        book, rate = _active_graph(transaction)
        duplicate = FeeRate(
            fee_code=rate.fee_code,
            fee_name=rate.fee_name,
            fee_type=rate.fee_type,
            currency=rate.currency,
            default_amount=rate.default_amount,
            enabled=rate.enabled,
            calc_mode=rate.calc_mode,
            allow_reduction=rate.allow_reduction,
            effective_from=rate.effective_from,
            effective_to=rate.effective_to,
            source_doc=rate.source_doc,
            source_url=rate.source_url,
            source_policy=rate.source_policy,
            source_version=rate.source_version,
            source_status=rate.source_status,
            official_rate_book_id=book.id,
        )
        transaction.add(duplicate)
        transaction.flush()

        error = _assert_error(409, lambda: _read(transaction))
        assert error.details == {"field": "rate"}


def test_repeated_reads_are_identical_and_call_no_write_or_activation(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _active_graph(transaction)
        unrelated = FeeRate(fee_code="UNRELATED_PENDING_ROW")
        transaction.add(unrelated)
        pending_before = tuple(transaction.new)
        dirty_before = tuple(transaction.dirty)
        deleted_before = tuple(transaction.deleted)
        flushes = 0

        def prohibited(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("read rule called a write/session-lifecycle operation")

        def count_flushes(*_args: object) -> None:
            nonlocal flushes
            flushes += 1

        event.listen(transaction, "before_flush", count_flushes)
        monkeypatch.setattr(transaction, "flush", prohibited)
        monkeypatch.setattr(transaction, "commit", prohibited)
        monkeypatch.setattr(transaction, "rollback", prohibited)
        monkeypatch.setattr(transaction, "begin_nested", prohibited)
        monkeypatch.setattr(official_rate_book, "activate_official_rate_book", prohibited)
        try:
            first = _read(transaction)
            second = _read(transaction)
        finally:
            event.remove(transaction, "before_flush", count_flushes)

        assert first == second
        assert tuple(transaction.new) == pending_before
        assert tuple(transaction.dirty) == dirty_before
        assert tuple(transaction.deleted) == deleted_before
        assert flushes == 0
