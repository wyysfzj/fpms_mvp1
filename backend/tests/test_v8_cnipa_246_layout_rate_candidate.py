from __future__ import annotations

import hashlib
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.fees.models import FeeRate, OfficialRateBook

try:
    from app.modules.fees.cnipa_layout_rate_candidate import (
        CNIPA_LAYOUT_246_DATA_SHA256,
        CNIPA_LAYOUT_246_SOURCE_SNAPSHOT,
        CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH,
        CnipaLayout246MaterializationDisposition,
        materialize_cnipa_layout_246,
    )
except ModuleNotFoundError:
    CNIPA_LAYOUT_246_DATA_SHA256 = ""
    CNIPA_LAYOUT_246_SOURCE_SNAPSHOT = ""
    CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH = ""

    class CnipaLayout246MaterializationDisposition:
        CREATED = "missing"
        REUSED = "missing"

    def materialize_cnipa_layout_246(_transaction: Session):
        pytest.fail("public CNIPA layout 246 materializer is missing")


BOOK_CODE = "CNIPA_LAYOUT_246"
VERSION = "2017-07-01"
FEE_CODE = "IC_LAYOUT_REGISTRATION_FEE"
SOURCE_URL = "https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html"
SOURCE_TITLE = "关于执行新的集成电路布图设计保护费收费标准的公告（第246号）"
NORMALIZED_SHA256 = "13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8"
PROVENANCE_SHA256 = "2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377"
SNAPSHOT_HASH = "f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4"
EXPECTED_SNAPSHOT = (
    '{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":['
    '{"content_sha256":"13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8",'
    '"document_no":"第二四六号","published_on":"2017-06-30",'
    '"retrieved_at":"2026-07-18T08:39:40Z",'
    f'"title":"{SOURCE_TITLE}","url":"{SOURCE_URL}"}}]}}'
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "backend/app/modules/fees/data/cnipa_246_layout_rate.json"
NORMALIZED_PATH = REPO_ROOT / "reference/cnipa/announcement_246_20170630.normalized.txt"
PROVENANCE_PATH = REPO_ROOT / "reference/cnipa/announcement_246_20170630.provenance.json"


def _assert_conflict(callable_) -> BusinessError:
    with pytest.raises(BusinessError) as caught:
        callable_()
    assert caught.value.status_code == 409
    assert caught.value.code == "CNIPA_LAYOUT_246_CANDIDATE_CONFLICT"
    return caught.value


def _graph(transaction: Session) -> tuple[OfficialRateBook, FeeRate]:
    book = transaction.scalar(
        select(OfficialRateBook).where(
            OfficialRateBook.source_authority == "CNIPA",
            OfficialRateBook.book_code == BOOK_CODE,
            OfficialRateBook.version_code == VERSION,
        )
    )
    assert book is not None
    rates = transaction.scalars(
        select(FeeRate).where(FeeRate.official_rate_book_id == book.id)
    ).all()
    assert len(rates) == 1
    return book, rates[0]


def _counts(transaction: Session) -> tuple[int, int]:
    return (
        transaction.scalar(
            select(func.count())
            .select_from(OfficialRateBook)
            .where(OfficialRateBook.book_code == BOOK_CODE)
        )
        or 0,
        transaction.scalar(
            select(func.count()).select_from(FeeRate).where(FeeRate.fee_code == FEE_CODE)
        )
        or 0,
    )


def test_materializes_exact_inactive_candidate_rate_and_locked_provenance(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        result = materialize_cnipa_layout_246(transaction)

        assert result.disposition is CnipaLayout246MaterializationDisposition.CREATED
        book, rate = _graph(transaction)
        assert result.rate_book_id == book.id
        assert result.rate_id == rate.id

        assert (
            book.source_authority,
            book.book_code,
            book.version_code,
            book.source_version,
        ) == ("CNIPA", BOOK_CODE, VERSION, VERSION)
        assert book.effective_from == date(2017, 7, 1)
        assert book.effective_to is None
        assert book.source_reference == SOURCE_URL
        assert book.source_published_on == date(2017, 6, 30)
        assert book.source_snapshot == EXPECTED_SNAPSHOT == CNIPA_LAYOUT_246_SOURCE_SNAPSHOT
        assert book.source_snapshot_hash == SNAPSHOT_HASH
        assert CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH == SNAPSHOT_HASH
        assert hashlib.sha256(book.source_snapshot.encode("utf-8")).hexdigest() == SNAPSHOT_HASH
        assert (
            book.approval_status,
            book.approved_by,
            book.approved_at,
            book.activation_status,
            book.activated_by,
            book.activated_at,
            book.current_identity_key,
        ) == ("PENDING", None, None, "INACTIVE", None, None, None)

        assert (
            rate.fee_code,
            rate.default_amount,
            rate.currency,
            rate.fee_type,
            rate.calc_mode,
            rate.allow_reduction,
            rate.enabled,
            rate.source_status,
            rate.official_rate_book_id,
        ) == (
            FEE_CODE,
            Decimal("1000.00"),
            "CNY",
            "GOV",
            "FIXED",
            False,
            True,
            "PENDING_CONFIRMATION",
            book.id,
        )
        assert rate.effective_from == date(2017, 7, 1)
        assert rate.effective_to is None
        assert rate.source_url == SOURCE_URL
        assert rate.source_version == VERSION

        assert hashlib.sha256(NORMALIZED_PATH.read_bytes()).hexdigest() == NORMALIZED_SHA256
        assert hashlib.sha256(PROVENANCE_PATH.read_bytes()).hexdigest() == PROVENANCE_SHA256
        assert hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() == CNIPA_LAYOUT_246_DATA_SHA256


def test_exact_replay_reuses_identities_without_insert_update_or_timestamp_churn(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        created = materialize_cnipa_layout_246(transaction)
        transaction.commit()

    with session_factory() as transaction:
        book_before, rate_before = _graph(transaction)
        identity_before = (
            book_before.id,
            rate_before.id,
            book_before.created_at,
            book_before.updated_at,
            rate_before.created_at,
            rate_before.updated_at,
        )
        before_flushes = 0

        def count_flushes(*_args: object) -> None:
            nonlocal before_flushes
            before_flushes += 1

        event.listen(transaction, "before_flush", count_flushes)
        try:
            reused = materialize_cnipa_layout_246(transaction)
        finally:
            event.remove(transaction, "before_flush", count_flushes)

        book_after, rate_after = _graph(transaction)
        assert created.rate_book_id == reused.rate_book_id == book_after.id
        assert created.rate_id == reused.rate_id == rate_after.id
        assert reused.disposition is CnipaLayout246MaterializationDisposition.REUSED
        assert (
            book_after.id,
            rate_after.id,
            book_after.created_at,
            book_after.updated_at,
            rate_after.created_at,
            rate_after.updated_at,
        ) == identity_before
        assert before_flushes == 0
        assert not transaction.new
        assert not transaction.dirty


@pytest.mark.parametrize(
    ("target", "field", "changed"),
    [
        ("book", "source_snapshot_hash", "0" * 64),
        ("book", "source_reference", "https://www.cnipa.gov.cn/changed"),
        ("rate", "fee_code", "IC_LAYOUT_REGISTRATION_FEE_CHANGED"),
        ("rate", "default_amount", Decimal("999.00")),
        ("rate", "currency", "USD"),
        ("rate", "fee_type", "SERVICE"),
        ("rate", "calc_mode", "TIER"),
        ("rate", "allow_reduction", True),
        ("rate", "enabled", False),
        ("rate", "source_status", "CONFIRMED"),
    ],
)
def test_changed_replay_is_409_and_preserves_precall_transaction_state(
    session_factory: sessionmaker,
    target: str,
    field: str,
    changed: object,
) -> None:
    with session_factory() as transaction:
        materialize_cnipa_layout_246(transaction)
        transaction.commit()

    with session_factory() as transaction:
        book, rate = _graph(transaction)
        row = book if target == "book" else rate
        setattr(row, field, changed)
        before = _counts(transaction)

        error = _assert_conflict(lambda: materialize_cnipa_layout_246(transaction))

        assert error.details == {"field": field}
        assert _counts(transaction) == before
        assert getattr(row, field) == changed


def test_missing_or_changed_adopted_source_fails_before_any_write(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import app.modules.fees.cnipa_layout_rate_candidate as candidate_module

    missing = tmp_path / "missing-normalized.txt"
    monkeypatch.setattr(candidate_module, "_NORMALIZED_SOURCE_PATH", missing)
    with session_factory() as transaction:
        _assert_conflict(lambda: materialize_cnipa_layout_246(transaction))
        assert _counts(transaction) == (0, 0)

    changed = tmp_path / "changed-normalized.txt"
    changed.write_bytes(NORMALIZED_PATH.read_bytes() + b"changed\n")
    monkeypatch.setattr(candidate_module, "_NORMALIZED_SOURCE_PATH", changed)
    with session_factory() as transaction:
        _assert_conflict(lambda: materialize_cnipa_layout_246(transaction))
        assert _counts(transaction) == (0, 0)


def test_materializer_never_commits_and_caller_rollback_persists_nothing(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:

        def prohibited_commit() -> None:
            raise AssertionError("materializer called commit")

        monkeypatch.setattr(transaction, "commit", prohibited_commit)
        materialize_cnipa_layout_246(transaction)
        assert _counts(transaction) == (1, 1)
        transaction.rollback()

    with session_factory() as verification:
        assert _counts(verification) == (0, 0)


def test_caller_commit_persists_the_complete_graph(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        result = materialize_cnipa_layout_246(transaction)
        transaction.commit()

    with session_factory() as verification:
        book, rate = _graph(verification)
        assert (book.id, rate.id) == (result.rate_book_id, result.rate_id)


def test_rate_insert_failure_rolls_back_only_materializer_savepoint(
    session_factory: sessionmaker,
) -> None:
    def fail_rate_insert(*_args: object) -> None:
        raise RuntimeError("forced rate insert failure")

    event.listen(FeeRate, "before_insert", fail_rate_insert)
    try:
        with session_factory() as transaction:
            with pytest.raises(RuntimeError, match="forced rate insert failure"):
                materialize_cnipa_layout_246(transaction)
            assert _counts(transaction) == (0, 0)
            assert transaction.is_active
    finally:
        event.remove(FeeRate, "before_insert", fail_rate_insert)


def test_candidate_stays_nonconsumable_and_module_exposes_no_activation_or_fallback(
    session_factory: sessionmaker,
) -> None:
    import app.modules.fees.cnipa_layout_rate_candidate as candidate_module

    with session_factory() as transaction:
        materialize_cnipa_layout_246(transaction)
        book, rate = _graph(transaction)
        assert book.approval_status == "PENDING"
        assert book.activation_status == "INACTIVE"
        assert book.current_identity_key is None
        assert rate.enabled is True
        assert rate.source_status == "PENDING_CONFIRMATION"

    assert set(candidate_module.__all__) == {
        "CNIPA_LAYOUT_246_DATA_SHA256",
        "CNIPA_LAYOUT_246_SOURCE_SNAPSHOT",
        "CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH",
        "CnipaLayout246MaterializationDisposition",
        "CnipaLayout246MaterializationResult",
        "materialize_cnipa_layout_246",
    }
    assert not hasattr(candidate_module, "activate")
    assert not hasattr(candidate_module, "seed")
    assert not hasattr(candidate_module, "fallback")
