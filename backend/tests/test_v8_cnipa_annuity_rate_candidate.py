from __future__ import annotations

import hashlib
import inspect
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.fees.models import FeeRate, OfficialRateBook

try:
    from app.modules.fees.cnipa_annuity_rate_candidate import (
        CNIPA_ANNUITY_DATA_SHA256,
        CNIPA_ANNUITY_SOURCE_SNAPSHOT,
        CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH,
        CnipaAnnuityMaterializationDisposition,
        materialize_cnipa_annuity_rate_candidate,
        parse_cnipa_annuity_tiers,
        select_cnipa_annuity_amount,
    )
except ModuleNotFoundError:
    CNIPA_ANNUITY_DATA_SHA256 = ""
    CNIPA_ANNUITY_SOURCE_SNAPSHOT = ""
    CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH = ""

    class CnipaAnnuityMaterializationDisposition:
        CREATED = "missing"
        REUSED = "missing"

    def materialize_cnipa_annuity_rate_candidate(_transaction: Session):
        pytest.fail("public CNIPA annuity candidate materializer is missing")

    def parse_cnipa_annuity_tiers(_fee_code: str, _calc_params: str):
        pytest.fail("public CNIPA annuity tier parser is missing")

    def select_cnipa_annuity_amount(_fee_code: str, _calc_params: str, _year_no: int):
        pytest.fail("public CNIPA annuity year selector is missing")


BOOK_CODE = "CNIPA_PATENT_ANNUITY_20260330"
VERSION = "2026-03-30"
SOURCE_TITLE = "专利和集成电路布图设计缴费服务指南"
METADATA_URL = "https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html"
PDF_URL = "https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"
PDF_SHA256 = "3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce"
SNAPSHOT_HASH = "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544"
EXPECTED_SNAPSHOT = (
    '{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":['
    '{"content_sha256":"3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce",'
    '"document_no":null,"published_on":"2026-03-30",'
    '"retrieved_at":"2026-07-19T03:55:57Z",'
    f'"title":"{SOURCE_TITLE}","url":"{PDF_URL}"}}]}}'
)
CALC_PARAMS = {
    "CN_ANNUITY_FEE_INV": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"900.00","from":1,"to":3},'
        '{"amount":"1200.00","from":4,"to":6},'
        '{"amount":"2000.00","from":7,"to":9},'
        '{"amount":"4000.00","from":10,"to":12},'
        '{"amount":"6000.00","from":13,"to":15},'
        '{"amount":"8000.00","from":16,"to":20}]}'
    ),
    "CN_ANNUITY_FEE_UM": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10}]}'
    ),
    "CN_ANNUITY_FEE_DES": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10},'
        '{"amount":"3000.00","from":11,"to":15}]}'
    ),
}
EXPECTED_TIERS = {
    "CN_ANNUITY_FEE_INV": (
        (1, 3, Decimal("900.00")),
        (4, 6, Decimal("1200.00")),
        (7, 9, Decimal("2000.00")),
        (10, 12, Decimal("4000.00")),
        (13, 15, Decimal("6000.00")),
        (16, 20, Decimal("8000.00")),
    ),
    "CN_ANNUITY_FEE_UM": (
        (1, 3, Decimal("600.00")),
        (4, 5, Decimal("900.00")),
        (6, 8, Decimal("1200.00")),
        (9, 10, Decimal("2000.00")),
    ),
    "CN_ANNUITY_FEE_DES": (
        (1, 3, Decimal("600.00")),
        (4, 5, Decimal("900.00")),
        (6, 8, Decimal("1200.00")),
        (9, 10, Decimal("2000.00")),
        (11, 15, Decimal("3000.00")),
    ),
}
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    REPO_ROOT / "backend/app/modules/fees/data/cnipa_payment_guide_20260330_annuity_rates.json"
)


def _assert_conflict(callable_) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        callable_()
    assert caught.value.status_code == 409
    assert caught.value.code == "CNIPA_ANNUITY_CANDIDATE_CONFLICT"
    return caught.value


def _graph(transaction: Session) -> tuple[OfficialRateBook, list[FeeRate]]:
    book = transaction.scalar(
        select(OfficialRateBook).where(
            OfficialRateBook.source_authority == "CNIPA",
            OfficialRateBook.book_code == BOOK_CODE,
            OfficialRateBook.version_code == VERSION,
        )
    )
    assert book is not None
    rates = transaction.scalars(
        select(FeeRate).where(FeeRate.official_rate_book_id == book.id).order_by(FeeRate.fee_code)
    ).all()
    return book, list(rates)


def _counts(transaction: Session) -> tuple[int, int]:
    return (
        transaction.scalar(
            select(func.count())
            .select_from(OfficialRateBook)
            .where(OfficialRateBook.book_code == BOOK_CODE)
        )
        or 0,
        transaction.scalar(
            select(func.count())
            .select_from(FeeRate)
            .where(FeeRate.fee_code.in_(tuple(CALC_PARAMS)))
        )
        or 0,
    )


def test_materializes_exact_inactive_candidate_and_three_linked_rates(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        result = materialize_cnipa_annuity_rate_candidate(transaction)
        book, rates = _graph(transaction)

        assert result.disposition is CnipaAnnuityMaterializationDisposition.CREATED
        assert result.rate_book_id == book.id
        assert result.rate_ids == tuple(rate.id for rate in rates)
        assert (
            book.source_authority,
            book.book_code,
            book.version_code,
            book.source_version,
        ) == ("CNIPA", BOOK_CODE, VERSION, VERSION)
        assert book.effective_from == date(2026, 3, 30)
        assert book.effective_to is None
        assert book.source_reference == PDF_URL
        assert book.source_published_on == date(2026, 3, 30)
        assert book.source_snapshot == EXPECTED_SNAPSHOT == CNIPA_ANNUITY_SOURCE_SNAPSHOT
        assert book.source_snapshot_hash == SNAPSHOT_HASH
        assert CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH == SNAPSHOT_HASH
        assert hashlib.sha256(book.source_snapshot.encode()).hexdigest() == SNAPSHOT_HASH
        assert (
            book.approval_status,
            book.approved_by,
            book.approved_at,
            book.activation_status,
            book.activated_by,
            book.activated_at,
            book.current_identity_key,
        ) == ("PENDING", None, None, "INACTIVE", None, None, None)

        assert len(rates) == 3
        for rate in rates:
            assert (
                rate.fee_type,
                rate.currency,
                rate.calc_mode,
                rate.enabled,
                rate.allow_reduction,
                rate.source_status,
                rate.default_amount,
                rate.official_rate_book_id,
            ) == (
                "GOV",
                "CNY",
                "TIER",
                True,
                True,
                "PENDING_CONFIRMATION",
                None,
                book.id,
            )
            assert rate.calc_params == CALC_PARAMS[rate.fee_code]
            assert rate.effective_from == date(2026, 3, 30)
            assert rate.effective_to is None
            assert rate.source_doc == SOURCE_TITLE
            assert rate.source_url == PDF_URL
            assert rate.source_policy is None
            assert rate.source_version == VERSION

        assert hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() == CNIPA_ANNUITY_DATA_SHA256
        payload = json.loads(DATA_PATH.read_bytes())
        assert payload["source"] == {
            "metadata_url": METADATA_URL,
            "pdf_bytes": 2478214,
            "pdf_pages": 32,
            "pdf_sha256": PDF_SHA256,
            "pdf_url": PDF_URL,
            "retrieved_at": "2026-07-19T03:55:57Z",
            "title": SOURCE_TITLE,
        }


@pytest.mark.parametrize(("fee_code", "expected"), EXPECTED_TIERS.items())
def test_public_parser_accepts_only_the_exact_frozen_tiers(
    fee_code: str,
    expected: tuple[tuple[int, int, Decimal], ...],
) -> None:
    tiers = parse_cnipa_annuity_tiers(fee_code, CALC_PARAMS[fee_code])

    assert tuple((tier.from_year, tier.to_year, tier.amount) for tier in tiers) == expected
    assert isinstance(tiers, tuple)


@pytest.mark.parametrize(("fee_code", "expected"), EXPECTED_TIERS.items())
def test_public_year_selector_returns_every_frozen_tier_amount(
    fee_code: str,
    expected: tuple[tuple[int, int, Decimal], ...],
) -> None:
    for start, end, amount in expected:
        for year_no in range(start, end + 1):
            assert select_cnipa_annuity_amount(fee_code, CALC_PARAMS[fee_code], year_no) == amount


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@pytest.mark.parametrize(
    ("fee_code", "calc_params"),
    [
        ("UNKNOWN", CALC_PARAMS["CN_ANNUITY_FEE_INV"]),
        ("CN_ANNUITY_FEE_INV", '{"schema":"CNIPA_ANNUITY_TIER_V1"}'),
        (
            "CN_ANNUITY_FEE_INV",
            '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[],"unknown":null}',
        ),
        (
            "CN_ANNUITY_FEE_INV",
            '{"tiers":[],"schema":"CNIPA_ANNUITY_TIER_V1"}',
        ),
        (
            "CN_ANNUITY_FEE_INV",
            CALC_PARAMS["CN_ANNUITY_FEE_INV"] + " ",
        ),
        (
            "CN_ANNUITY_FEE_INV",
            CALC_PARAMS["CN_ANNUITY_FEE_INV"].replace(
                "CNIPA_ANNUITY_TIER_V1", "CNIPA_ANNUITY_TIER_V2"
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":null}',
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [{"amount": "900.00", "from": True, "to": 20}],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [{"amount": "900.00", "from": 1, "to": "20"}],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [{"amount": "900", "from": 1, "to": 20}],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [{"amount": "0.00", "from": 1, "to": 20}],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{"from":1,"amount":"900.00","to":20}]}',
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [
                        {"amount": "900.00", "from": 1, "to": 3},
                        {"amount": "1200.00", "from": 5, "to": 20},
                    ],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [
                        {"amount": "900.00", "from": 1, "to": 3},
                        {"amount": "1200.00", "from": 3, "to": 20},
                    ],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [
                        {"amount": "1200.00", "from": 4, "to": 20},
                        {"amount": "900.00", "from": 1, "to": 3},
                    ],
                }
            ),
        ),
        (
            "CN_ANNUITY_FEE_INV",
            _canonical(
                {
                    "schema": "CNIPA_ANNUITY_TIER_V1",
                    "tiers": [{"amount": "900.00", "from": 1, "to": 19}],
                }
            ),
        ),
    ],
)
def test_parser_rejects_noncanonical_or_invalid_tiers_with_deterministic_409(
    fee_code: str,
    calc_params: str,
) -> None:
    first = _assert_conflict(lambda: parse_cnipa_annuity_tiers(fee_code, calc_params))
    second = _assert_conflict(lambda: parse_cnipa_annuity_tiers(fee_code, calc_params))

    assert (first.message, first.details) == (second.message, second.details)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_parser_rejects_nonfinite_json_constants_with_deterministic_409(
    constant: str,
) -> None:
    calc_params = (
        f'{{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":[{{"amount":{constant},"from":1,"to":20}}]}}'
    )

    first = _assert_conflict(lambda: parse_cnipa_annuity_tiers("CN_ANNUITY_FEE_INV", calc_params))
    second = _assert_conflict(lambda: parse_cnipa_annuity_tiers("CN_ANNUITY_FEE_INV", calc_params))

    assert (first.message, first.details) == (second.message, second.details)


@pytest.mark.parametrize("year_no", [0, -1, 21, True, "1", None])
def test_year_selector_rejects_wrong_type_or_out_of_range_without_selection(
    year_no: object,
) -> None:
    _assert_conflict(
        lambda: select_cnipa_annuity_amount(
            "CN_ANNUITY_FEE_INV",
            CALC_PARAMS["CN_ANNUITY_FEE_INV"],
            year_no,
        )
    )


def test_exact_replay_reuses_complete_graph_without_flush_or_timestamp_churn(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        created = materialize_cnipa_annuity_rate_candidate(transaction)
        transaction.commit()

    with session_factory() as transaction:
        book_before, rates_before = _graph(transaction)
        identity_before = (
            book_before.id,
            book_before.created_at,
            book_before.updated_at,
            tuple((rate.id, rate.created_at, rate.updated_at) for rate in rates_before),
        )
        flushes = 0

        def count_flushes(*_args: object) -> None:
            nonlocal flushes
            flushes += 1

        event.listen(transaction, "before_flush", count_flushes)
        try:
            reused = materialize_cnipa_annuity_rate_candidate(transaction)
        finally:
            event.remove(transaction, "before_flush", count_flushes)

        book_after, rates_after = _graph(transaction)
        assert reused.disposition is CnipaAnnuityMaterializationDisposition.REUSED
        assert reused.rate_book_id == created.rate_book_id == book_after.id
        assert reused.rate_ids == created.rate_ids == tuple(rate.id for rate in rates_after)
        assert (
            book_after.id,
            book_after.created_at,
            book_after.updated_at,
            tuple((rate.id, rate.created_at, rate.updated_at) for rate in rates_after),
        ) == identity_before
        assert flushes == 0
        assert not transaction.new
        assert not transaction.dirty


@pytest.mark.parametrize(
    ("target", "field", "changed"),
    [
        ("book", "source_snapshot_hash", "0" * 64),
        ("book", "source_reference", METADATA_URL),
        ("book", "approval_status", "APPROVED"),
        ("book", "activation_status", "ACTIVE"),
        ("rate", "calc_params", CALC_PARAMS["CN_ANNUITY_FEE_INV"] + " "),
        ("rate", "currency", "USD"),
        ("rate", "fee_type", "SERVICE"),
        ("rate", "calc_mode", "FIXED"),
        ("rate", "allow_reduction", False),
        ("rate", "enabled", False),
        ("rate", "source_status", "CONFIRMED"),
        ("rate", "official_rate_book_id", None),
    ],
)
def test_changed_replay_is_409_and_does_not_repair_the_graph(
    session_factory: sessionmaker,
    target: str,
    field: str,
    changed: object,
) -> None:
    with session_factory() as transaction:
        materialize_cnipa_annuity_rate_candidate(transaction)
        transaction.commit()

    with session_factory() as transaction:
        book, rates = _graph(transaction)
        row = book if target == "book" else rates[0]
        setattr(row, field, changed)

        error = _assert_conflict(lambda: materialize_cnipa_annuity_rate_candidate(transaction))

        assert error.details == {"field": field}
        assert getattr(row, field) == changed
        assert not transaction.new


def test_missing_or_extra_replay_rate_is_409_without_repair(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        materialize_cnipa_annuity_rate_candidate(transaction)
        transaction.commit()

    with session_factory() as transaction:
        _book, rates = _graph(transaction)
        transaction.delete(rates[0])
        transaction.commit()

    with session_factory() as transaction:
        _assert_conflict(lambda: materialize_cnipa_annuity_rate_candidate(transaction))
        assert _counts(transaction) == (1, 2)

    with session_factory() as transaction:
        book, _rates = _graph(transaction)
        transaction.add(
            FeeRate(
                fee_code="CN_ANNUITY_FEE_EXTRA",
                fee_type="GOV",
                currency="CNY",
                calc_mode="TIER",
                enabled=True,
                allow_reduction=True,
                source_status="PENDING_CONFIRMATION",
                official_rate_book_id=book.id,
            )
        )
        transaction.commit()

    with session_factory() as transaction:
        _assert_conflict(lambda: materialize_cnipa_annuity_rate_candidate(transaction))
        book, rates = _graph(transaction)
        assert len(rates) == 3
        assert {rate.fee_code for rate in rates} == {
            "CN_ANNUITY_FEE_EXTRA",
            "CN_ANNUITY_FEE_INV",
            "CN_ANNUITY_FEE_UM",
        }


def test_changed_canonical_data_fails_before_any_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import app.modules.fees.cnipa_annuity_rate_candidate as candidate_module

    changed = tmp_path / "changed-annuity-data.json"
    changed.write_bytes(DATA_PATH.read_bytes() + b" ")
    monkeypatch.setattr(candidate_module, "_DATA_PATH", changed)

    with session_factory() as transaction:
        _assert_conflict(lambda: materialize_cnipa_annuity_rate_candidate(transaction))
        assert _counts(transaction) == (0, 0)


def test_materializer_never_commits_rolls_back_or_closes_caller_session(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = session_factory()

    def prohibited() -> None:
        raise AssertionError("materializer changed caller transaction ownership")

    monkeypatch.setattr(transaction, "commit", prohibited)
    monkeypatch.setattr(transaction, "rollback", prohibited)
    monkeypatch.setattr(transaction, "close", prohibited)
    materialize_cnipa_annuity_rate_candidate(transaction)
    assert _counts(transaction) == (1, 3)
    monkeypatch.undo()
    transaction.rollback()
    transaction.close()

    with session_factory() as verification:
        assert _counts(verification) == (0, 0)


def test_caller_commit_persists_the_complete_candidate_graph(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        result = materialize_cnipa_annuity_rate_candidate(transaction)
        transaction.commit()

    with session_factory() as verification:
        book, rates = _graph(verification)
        assert result.rate_book_id == book.id
        assert result.rate_ids == tuple(rate.id for rate in rates)
        assert _counts(verification) == (1, 3)


def test_rate_insert_failure_rolls_back_the_materializer_savepoint_only(
    session_factory: sessionmaker,
) -> None:
    def fail_second_rate(_mapper: object, _connection: object, target: FeeRate) -> None:
        if target.fee_code == "CN_ANNUITY_FEE_UM":
            raise RuntimeError("forced annuity rate insert failure")

    event.listen(FeeRate, "before_insert", fail_second_rate)
    try:
        with session_factory() as transaction:
            with pytest.raises(RuntimeError, match="forced annuity rate insert failure"):
                materialize_cnipa_annuity_rate_candidate(transaction)
            assert _counts(transaction) == (0, 0)
            assert transaction.is_active
    finally:
        event.remove(FeeRate, "before_insert", fail_second_rate)


def test_module_exposes_no_activation_runtime_fallback_or_wall_clock_path(
    session_factory: sessionmaker,
) -> None:
    import app.modules.fees.cnipa_annuity_rate_candidate as candidate_module

    with session_factory() as transaction:
        materialize_cnipa_annuity_rate_candidate(transaction)
        book, rates = _graph(transaction)
        assert book.approval_status == "PENDING"
        assert book.activation_status == "INACTIVE"
        assert book.current_identity_key is None
        assert all(rate.source_status == "PENDING_CONFIRMATION" for rate in rates)

    assert set(candidate_module.__all__) == {
        "CNIPA_ANNUITY_DATA_SHA256",
        "CNIPA_ANNUITY_SOURCE_SNAPSHOT",
        "CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH",
        "CnipaAnnuityMaterializationDisposition",
        "CnipaAnnuityMaterializationResult",
        "CnipaAnnuityTier",
        "materialize_cnipa_annuity_rate_candidate",
        "parse_cnipa_annuity_tiers",
        "select_cnipa_annuity_amount",
    }
    assert not hasattr(candidate_module, "activate")
    assert not hasattr(candidate_module, "seed")
    assert not hasattr(candidate_module, "fallback")
    source = inspect.getsource(candidate_module)
    assert "date.today(" not in source
    assert "legacy" not in source.lower()
    assert "tianyue" not in source.lower()
