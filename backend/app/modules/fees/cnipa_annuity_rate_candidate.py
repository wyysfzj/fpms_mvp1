from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import Enum
from pathlib import Path
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.fees.models import FeeRate, OfficialRateBook

__all__ = (
    "CNIPA_ANNUITY_DATA_SHA256",
    "CNIPA_ANNUITY_SOURCE_SNAPSHOT",
    "CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH",
    "CnipaAnnuityMaterializationDisposition",
    "CnipaAnnuityMaterializationResult",
    "CnipaAnnuityTier",
    "materialize_cnipa_annuity_rate_candidate",
    "parse_cnipa_annuity_tiers",
    "select_cnipa_annuity_amount",
)

CNIPA_ANNUITY_DATA_SHA256 = "c2d43de97be37f6263a74e81ab19e525025b94ac937d8b6de6fd1d2f2e480ba3"
CNIPA_ANNUITY_SOURCE_SNAPSHOT = (
    '{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":['
    '{"content_sha256":"3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce",'
    '"document_no":null,"published_on":"2026-03-30",'
    '"retrieved_at":"2026-07-19T03:55:57Z",'
    '"title":"专利和集成电路布图设计缴费服务指南",'
    '"url":"https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"}]}'
)
CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH = (
    "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544"
)

_BOOK_CODE = "CNIPA_PATENT_ANNUITY_20260330"
_VERSION = "2026-03-30"
_SOURCE_TITLE = "专利和集成电路布图设计缴费服务指南"
_METADATA_URL = "https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html"
_PDF_URL = "https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"
_PDF_SHA256 = "3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce"
_DATA_PATH = Path(__file__).with_name("data") / ("cnipa_payment_guide_20260330_annuity_rates.json")
_AMOUNT_PATTERN = re.compile(r"[1-9]\d*\.\d{2}\Z")
_FINAL_YEAR_BY_FEE_CODE = {
    "CN_ANNUITY_FEE_DES": 15,
    "CN_ANNUITY_FEE_INV": 20,
    "CN_ANNUITY_FEE_UM": 10,
}
_CALC_PARAMS = {
    "CN_ANNUITY_FEE_DES": (
        '{"schema":"CNIPA_ANNUITY_TIER_V1","tiers":['
        '{"amount":"600.00","from":1,"to":3},'
        '{"amount":"900.00","from":4,"to":5},'
        '{"amount":"1200.00","from":6,"to":8},'
        '{"amount":"2000.00","from":9,"to":10},'
        '{"amount":"3000.00","from":11,"to":15}]}'
    ),
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
}
_EXPECTED_BOOK = {
    "activation_status": "INACTIVE",
    "approval_status": "PENDING",
    "book_code": _BOOK_CODE,
    "effective_from": _VERSION,
    "effective_to": None,
    "source_authority": "CNIPA",
    "source_published_on": _VERSION,
    "source_reference": _PDF_URL,
    "source_snapshot_hash": CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH,
    "source_version": _VERSION,
    "version_code": _VERSION,
}
_EXPECTED_SOURCE = {
    "metadata_url": _METADATA_URL,
    "pdf_bytes": 2478214,
    "pdf_pages": 32,
    "pdf_sha256": _PDF_SHA256,
    "pdf_url": _PDF_URL,
    "retrieved_at": "2026-07-19T03:55:57Z",
    "title": _SOURCE_TITLE,
}
_EXPECTED_RATES = tuple(
    {
        "allow_reduction": True,
        "calc_mode": "TIER",
        "calc_params": _CALC_PARAMS[fee_code],
        "currency": "CNY",
        "effective_from": _VERSION,
        "effective_to": None,
        "enabled": True,
        "fee_code": fee_code,
        "fee_type": "GOV",
        "source_doc": _SOURCE_TITLE,
        "source_policy": None,
        "source_status": "PENDING_CONFIRMATION",
        "source_url": _PDF_URL,
        "source_version": _VERSION,
    }
    for fee_code in sorted(_CALC_PARAMS)
)


class CnipaAnnuityMaterializationDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class CnipaAnnuityTier:
    from_year: int
    to_year: int
    amount: Decimal


@dataclass(frozen=True)
class CnipaAnnuityMaterializationResult:
    rate_book_id: str
    rate_ids: tuple[str, ...]
    disposition: CnipaAnnuityMaterializationDisposition


def _conflict(field: str) -> NoReturn:
    raise_business_error(
        "CNIPA_ANNUITY_CANDIDATE_CONFLICT",
        "CNIPA annuity candidate conflicts with the frozen contract",
        details={"field": field},
        status_code=409,
    )


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _reject_nonfinite_json_constant(_constant: str) -> NoReturn:
    _conflict("calc_params")


def parse_cnipa_annuity_tiers(
    fee_code: str,
    calc_params: str,
) -> tuple[CnipaAnnuityTier, ...]:
    if type(fee_code) is not str or fee_code not in _FINAL_YEAR_BY_FEE_CODE:
        _conflict("fee_code")
    if type(calc_params) is not str:
        _conflict("calc_params")
    try:
        payload = json.loads(
            calc_params,
            parse_constant=_reject_nonfinite_json_constant,
        )
    except (UnicodeError, ValueError):
        _conflict("calc_params")
    if (
        type(payload) is not dict
        or set(payload) != {"schema", "tiers"}
        or payload.get("schema") != "CNIPA_ANNUITY_TIER_V1"
        or type(payload.get("tiers")) is not list
        or _canonical_json(payload) != calc_params
    ):
        _conflict("calc_params")

    parsed: list[CnipaAnnuityTier] = []
    expected_from = 1
    for raw_tier in payload["tiers"]:
        if type(raw_tier) is not dict or set(raw_tier) != {"amount", "from", "to"}:
            _conflict("calc_params")
        from_year = raw_tier.get("from")
        to_year = raw_tier.get("to")
        amount_text = raw_tier.get("amount")
        if (
            type(from_year) is not int
            or type(to_year) is not int
            or from_year != expected_from
            or from_year <= 0
            or to_year < from_year
            or type(amount_text) is not str
            or _AMOUNT_PATTERN.fullmatch(amount_text) is None
        ):
            _conflict("calc_params")
        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            _conflict("calc_params")
        if amount <= 0:
            _conflict("calc_params")
        parsed.append(
            CnipaAnnuityTier(
                from_year=from_year,
                to_year=to_year,
                amount=amount,
            )
        )
        expected_from = to_year + 1

    if not parsed or parsed[-1].to_year != _FINAL_YEAR_BY_FEE_CODE[fee_code]:
        _conflict("calc_params")
    return tuple(parsed)


def select_cnipa_annuity_amount(
    fee_code: str,
    calc_params: str,
    year_no: int,
) -> Decimal:
    if type(year_no) is not int or year_no <= 0:
        _conflict("year_no")
    tiers = parse_cnipa_annuity_tiers(fee_code, calc_params)
    for tier in tiers:
        if tier.from_year <= year_no <= tier.to_year:
            return tier.amount
    _conflict("year_no")


def _read_frozen_data() -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    try:
        data_bytes = _DATA_PATH.read_bytes()
    except OSError:
        _conflict("canonical_data")
    if hashlib.sha256(data_bytes).hexdigest() != CNIPA_ANNUITY_DATA_SHA256:
        _conflict("canonical_data")
    try:
        payload = json.loads(data_bytes)
    except (UnicodeError, ValueError):
        _conflict("canonical_data")
    if (
        type(payload) is not dict
        or set(payload) != {"book", "rates", "schema_version", "source"}
        or payload.get("schema_version") != "CNIPA_ANNUITY_RATE_CANDIDATE_V1"
        or payload.get("book") != _EXPECTED_BOOK
        or payload.get("rates") != list(_EXPECTED_RATES)
        or payload.get("source") != _EXPECTED_SOURCE
        or data_bytes != f"{_canonical_json(payload)}\n".encode()
    ):
        _conflict("canonical_data")

    source = payload["source"]
    snapshot = _canonical_json(
        {
            "schema_version": "CNIPA_RATE_SOURCE_V1",
            "sources": [
                {
                    "content_sha256": source["pdf_sha256"],
                    "document_no": None,
                    "published_on": _VERSION,
                    "retrieved_at": source["retrieved_at"],
                    "title": source["title"],
                    "url": source["pdf_url"],
                }
            ],
        }
    )
    if (
        snapshot != CNIPA_ANNUITY_SOURCE_SNAPSHOT
        or hashlib.sha256(snapshot.encode()).hexdigest() != CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH
    ):
        _conflict("source_snapshot")
    for rate in _EXPECTED_RATES:
        parse_cnipa_annuity_tiers(rate["fee_code"], rate["calc_params"])
    return payload["book"], tuple(payload["rates"])


def _first_mismatch(row: object, expected: dict[str, object]) -> str | None:
    for field, value in expected.items():
        if getattr(row, field) != value:
            return field
    return None


def _book_values() -> dict[str, object]:
    return {
        "book_code": _BOOK_CODE,
        "version_code": _VERSION,
        "source_authority": "CNIPA",
        "source_reference": _PDF_URL,
        "source_version": _VERSION,
        "source_published_on": date(2026, 3, 30),
        "source_snapshot": CNIPA_ANNUITY_SOURCE_SNAPSHOT,
        "source_snapshot_hash": CNIPA_ANNUITY_SOURCE_SNAPSHOT_HASH,
        "approval_status": "PENDING",
        "approved_by": None,
        "approved_at": None,
        "effective_from": date(2026, 3, 30),
        "effective_to": None,
        "activation_status": "INACTIVE",
        "activated_by": None,
        "activated_at": None,
        "current_identity_key": None,
    }


def _rate_values(rate: dict[str, object], book_id: str) -> dict[str, object]:
    return {
        "fee_code": rate["fee_code"],
        "fee_name": None,
        "fee_type": rate["fee_type"],
        "currency": rate["currency"],
        "default_amount": None,
        "enabled": rate["enabled"],
        "rate_group": None,
        "country_code": None,
        "case_type": None,
        "patent_category": None,
        "fee_domain": None,
        "fee_section": None,
        "fee_category": None,
        "fee_subtype": None,
        "reduction_scope": None,
        "calc_mode": rate["calc_mode"],
        "calc_params": rate["calc_params"],
        "allow_reduction": rate["allow_reduction"],
        "effective_from": date(2026, 3, 30),
        "effective_to": None,
        "source_doc": rate["source_doc"],
        "source_url": rate["source_url"],
        "source_policy": rate["source_policy"],
        "source_version": rate["source_version"],
        "source_status": rate["source_status"],
        "official_rate_book_id": book_id,
    }


def _replay_result(
    transaction: Session,
    book: OfficialRateBook,
    rates_data: tuple[dict[str, object], ...],
) -> CnipaAnnuityMaterializationResult:
    mismatch = _first_mismatch(book, _book_values())
    if mismatch is not None:
        _conflict(mismatch)

    rates = transaction.scalars(
        select(FeeRate).where(FeeRate.official_rate_book_id == book.id).order_by(FeeRate.fee_code)
    ).all()
    if len(rates) != len(rates_data):
        _conflict("linked_rates")
    for row, expected_data in zip(rates, rates_data, strict=True):
        mismatch = _first_mismatch(row, _rate_values(expected_data, book.id))
        if mismatch is not None:
            _conflict(mismatch)
    return CnipaAnnuityMaterializationResult(
        rate_book_id=book.id,
        rate_ids=tuple(row.id for row in rates),
        disposition=CnipaAnnuityMaterializationDisposition.REUSED,
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if not driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def materialize_cnipa_annuity_rate_candidate(
    transaction: Session,
) -> CnipaAnnuityMaterializationResult:
    if not isinstance(transaction, Session):
        raise_business_error(
            "CNIPA_ANNUITY_CANDIDATE_INVALID_INPUT",
            "A SQLAlchemy caller transaction is required",
            details={"field": "transaction"},
            status_code=400,
        )
    _book_data, rates_data = _read_frozen_data()

    with transaction.no_autoflush:
        books = transaction.scalars(
            select(OfficialRateBook).where(
                OfficialRateBook.source_authority == "CNIPA",
                OfficialRateBook.book_code == _BOOK_CODE,
                OfficialRateBook.version_code == _VERSION,
            )
        ).all()
        if books:
            if len(books) != 1:
                _conflict("book_code")
            return _replay_result(transaction, books[0], rates_data)

    _ensure_sqlite_outer_transaction(transaction)
    with transaction.begin_nested():
        book = OfficialRateBook(**_book_values())
        transaction.add(book)
        transaction.flush([book])

        rates = [FeeRate(**_rate_values(rate_data, book.id)) for rate_data in rates_data]
        transaction.add_all(rates)
        transaction.flush(rates)

    return CnipaAnnuityMaterializationResult(
        rate_book_id=book.id,
        rate_ids=tuple(rate.id for rate in rates),
        disposition=CnipaAnnuityMaterializationDisposition.CREATED,
    )
