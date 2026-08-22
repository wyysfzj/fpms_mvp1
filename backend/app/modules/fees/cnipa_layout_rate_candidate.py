from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.fees.models import FeeRate, OfficialRateBook

__all__ = (
    "CNIPA_LAYOUT_246_DATA_SHA256",
    "CNIPA_LAYOUT_246_SOURCE_SNAPSHOT",
    "CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH",
    "CnipaLayout246MaterializationDisposition",
    "CnipaLayout246MaterializationResult",
    "materialize_cnipa_layout_246",
)

CNIPA_LAYOUT_246_DATA_SHA256 = "4d7756b3656db9b9184903f794002fd73396105b9392fbcf61c977ec71337d40"
CNIPA_LAYOUT_246_SOURCE_SNAPSHOT = (
    '{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":['
    '{"content_sha256":"13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8",'
    '"document_no":"第二四六号","published_on":"2017-06-30",'
    '"retrieved_at":"2026-07-18T08:39:40Z",'
    '"title":"关于执行新的集成电路布图设计保护费收费标准的公告（第246号）",'
    '"url":"https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html"}]}'
)
CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH = (
    "f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4"
)

_BOOK_CODE = "CNIPA_LAYOUT_246"
_VERSION = "2017-07-01"
_FEE_CODE = "IC_LAYOUT_REGISTRATION_FEE"
_SOURCE_URL = "https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html"
_SOURCE_TITLE = "关于执行新的集成电路布图设计保护费收费标准的公告（第246号）"
_DOCUMENT_NUMBER = "第二四六号"
_NORMALIZED_SHA256 = "13a487ed0575e86412830420fdb652d93ba0a8eb915bfeecd02097d75631d2b8"
_PROVENANCE_SHA256 = "2ff9eb7e84253359b2075e972bdd955313b95955f0ebad5e3d1b9fe9ec642377"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DATA_PATH = Path(__file__).with_name("data") / "cnipa_246_layout_rate.json"
_NORMALIZED_SOURCE_PATH = _REPO_ROOT / "reference/cnipa/announcement_246_20170630.normalized.txt"
_PROVENANCE_SOURCE_PATH = _REPO_ROOT / "reference/cnipa/announcement_246_20170630.provenance.json"

_EXPECTED_SOURCES = {
    "normalized_path": "reference/cnipa/announcement_246_20170630.normalized.txt",
    "normalized_sha256": _NORMALIZED_SHA256,
    "provenance_path": "reference/cnipa/announcement_246_20170630.provenance.json",
    "provenance_sha256": _PROVENANCE_SHA256,
}
_EXPECTED_PROVENANCE = {
    "content_sha256": _NORMALIZED_SHA256,
    "document_number": _DOCUMENT_NUMBER,
    "effective_from": _VERSION,
    "published_on": "2017-06-30",
    "retrieval_method": "normalized-primary-page-excerpt",
    "retrieved_at": "2026-07-18T08:39:40Z",
    "source_url": _SOURCE_URL,
    "title": _SOURCE_TITLE,
}
_EXPECTED_BOOK = {
    "activation_status": "INACTIVE",
    "approval_status": "PENDING",
    "book_code": _BOOK_CODE,
    "effective_from": _VERSION,
    "effective_to": None,
    "source_authority": "CNIPA",
    "source_published_on": "2017-06-30",
    "source_reference": _SOURCE_URL,
    "source_snapshot_hash": CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH,
    "source_version": _VERSION,
    "version_code": _VERSION,
}
_EXPECTED_RATE = {
    "allow_reduction": False,
    "calc_mode": "FIXED",
    "currency": "CNY",
    "default_amount": "1000.00",
    "effective_from": _VERSION,
    "effective_to": None,
    "enabled": True,
    "fee_code": _FEE_CODE,
    "fee_type": "GOV",
    "source_doc": _SOURCE_TITLE,
    "source_policy": _DOCUMENT_NUMBER,
    "source_status": "PENDING_CONFIRMATION",
    "source_url": _SOURCE_URL,
    "source_version": _VERSION,
}


class CnipaLayout246MaterializationDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class CnipaLayout246MaterializationResult:
    rate_book_id: str
    rate_id: str
    disposition: CnipaLayout246MaterializationDisposition


def _conflict(field: str) -> NoReturn:
    raise_business_error(
        "CNIPA_LAYOUT_246_CANDIDATE_CONFLICT",
        "CNIPA layout 246 candidate conflicts with the frozen contract",
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


def _read_locked(path: Path, expected_sha256: str, field: str) -> bytes:
    try:
        content = path.read_bytes()
    except OSError:
        _conflict(field)
    if hashlib.sha256(content).hexdigest() != expected_sha256:
        _conflict(field)
    return content


def _load_frozen_data() -> tuple[dict[str, object], dict[str, object]]:
    data_bytes = _read_locked(_DATA_PATH, CNIPA_LAYOUT_246_DATA_SHA256, "canonical_data")
    try:
        payload = json.loads(data_bytes)
    except (UnicodeDecodeError, ValueError):
        _conflict("canonical_data")
    if (
        type(payload) is not dict
        or set(payload) != {"book", "rate", "schema_version", "sources"}
        or payload.get("schema_version") != "CNIPA_LAYOUT_246_RATE_CANDIDATE_V1"
        or payload.get("book") != _EXPECTED_BOOK
        or payload.get("rate") != _EXPECTED_RATE
        or payload.get("sources") != _EXPECTED_SOURCES
        or data_bytes != f"{_canonical_json(payload)}\n".encode()
    ):
        _conflict("canonical_data")

    normalized = _read_locked(
        _NORMALIZED_SOURCE_PATH,
        _NORMALIZED_SHA256,
        "normalized_source",
    )
    provenance_bytes = _read_locked(
        _PROVENANCE_SOURCE_PATH,
        _PROVENANCE_SHA256,
        "source_provenance",
    )
    try:
        provenance = json.loads(provenance_bytes)
    except (UnicodeDecodeError, ValueError):
        _conflict("source_provenance")
    if (
        provenance != _EXPECTED_PROVENANCE
        or provenance_bytes != f"{_canonical_json(provenance)}\n".encode()
        or hashlib.sha256(normalized).hexdigest() != provenance["content_sha256"]
    ):
        _conflict("source_provenance")

    snapshot = _canonical_json(
        {
            "schema_version": "CNIPA_RATE_SOURCE_V1",
            "sources": [
                {
                    "content_sha256": provenance["content_sha256"],
                    "document_no": provenance["document_number"],
                    "published_on": provenance["published_on"],
                    "retrieved_at": provenance["retrieved_at"],
                    "title": provenance["title"],
                    "url": provenance["source_url"],
                }
            ],
        }
    )
    if (
        snapshot != CNIPA_LAYOUT_246_SOURCE_SNAPSHOT
        or hashlib.sha256(snapshot.encode()).hexdigest() != CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH
    ):
        _conflict("source_snapshot")
    return payload["book"], payload["rate"]


def _first_mismatch(row: object, expected: dict[str, object]) -> str | None:
    for field, value in expected.items():
        if getattr(row, field) != value:
            return field
    return None


def _replay_result(
    transaction: Session,
    book: OfficialRateBook,
) -> CnipaLayout246MaterializationResult:
    book_expected = {
        "book_code": _BOOK_CODE,
        "version_code": _VERSION,
        "source_authority": "CNIPA",
        "source_reference": _SOURCE_URL,
        "source_version": _VERSION,
        "source_published_on": date(2017, 6, 30),
        "source_snapshot": CNIPA_LAYOUT_246_SOURCE_SNAPSHOT,
        "source_snapshot_hash": CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH,
        "approval_status": "PENDING",
        "approved_by": None,
        "approved_at": None,
        "effective_from": date(2017, 7, 1),
        "effective_to": None,
        "activation_status": "INACTIVE",
        "activated_by": None,
        "activated_at": None,
        "current_identity_key": None,
    }
    mismatch = _first_mismatch(book, book_expected)
    if mismatch is not None:
        _conflict(mismatch)

    rates = transaction.scalars(
        select(FeeRate).where(FeeRate.official_rate_book_id == book.id)
    ).all()
    if len(rates) != 1:
        _conflict("linked_rates")
    rate = rates[0]
    rate_expected = {
        "fee_code": _FEE_CODE,
        "fee_name": None,
        "fee_type": "GOV",
        "currency": "CNY",
        "default_amount": Decimal("1000.00"),
        "enabled": True,
        "rate_group": None,
        "country_code": None,
        "case_type": None,
        "patent_category": None,
        "fee_domain": None,
        "fee_section": None,
        "fee_category": None,
        "fee_subtype": None,
        "reduction_scope": None,
        "calc_mode": "FIXED",
        "calc_params": None,
        "allow_reduction": False,
        "effective_from": date(2017, 7, 1),
        "effective_to": None,
        "source_doc": _SOURCE_TITLE,
        "source_url": _SOURCE_URL,
        "source_policy": _DOCUMENT_NUMBER,
        "source_version": _VERSION,
        "source_status": "PENDING_CONFIRMATION",
        "official_rate_book_id": book.id,
    }
    mismatch = _first_mismatch(rate, rate_expected)
    if mismatch is not None:
        _conflict(mismatch)
    return CnipaLayout246MaterializationResult(
        rate_book_id=book.id,
        rate_id=rate.id,
        disposition=CnipaLayout246MaterializationDisposition.REUSED,
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    driver_connection = connection.connection.driver_connection
    if not driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def materialize_cnipa_layout_246(
    transaction: Session,
) -> CnipaLayout246MaterializationResult:
    if not isinstance(transaction, Session):
        raise_business_error(
            "CNIPA_LAYOUT_246_CANDIDATE_INVALID_INPUT",
            "A SQLAlchemy caller transaction is required",
            details={"field": "transaction"},
            status_code=400,
        )
    _load_frozen_data()

    with transaction.no_autoflush:
        books = transaction.scalars(
            select(OfficialRateBook).where(
                OfficialRateBook.source_authority == "CNIPA",
                OfficialRateBook.book_code == _BOOK_CODE,
            )
        ).all()
        if books:
            if len(books) != 1:
                _conflict("book_code")
            return _replay_result(transaction, books[0])

    _ensure_sqlite_outer_transaction(transaction)
    with transaction.begin_nested():
        book = OfficialRateBook(
            book_code=_BOOK_CODE,
            version_code=_VERSION,
            source_authority="CNIPA",
            source_reference=_SOURCE_URL,
            source_version=_VERSION,
            source_published_on=date(2017, 6, 30),
            source_snapshot=CNIPA_LAYOUT_246_SOURCE_SNAPSHOT,
            source_snapshot_hash=CNIPA_LAYOUT_246_SOURCE_SNAPSHOT_HASH,
            approval_status="PENDING",
            approved_by=None,
            approved_at=None,
            effective_from=date(2017, 7, 1),
            effective_to=None,
            activation_status="INACTIVE",
            activated_by=None,
            activated_at=None,
            current_identity_key=None,
        )
        transaction.add(book)
        transaction.flush([book])

        rate = FeeRate(
            fee_code=_FEE_CODE,
            fee_name=None,
            fee_type="GOV",
            currency="CNY",
            default_amount=Decimal("1000.00"),
            enabled=True,
            rate_group=None,
            country_code=None,
            case_type=None,
            patent_category=None,
            fee_domain=None,
            fee_section=None,
            fee_category=None,
            fee_subtype=None,
            reduction_scope=None,
            calc_mode="FIXED",
            calc_params=None,
            allow_reduction=False,
            effective_from=date(2017, 7, 1),
            effective_to=None,
            source_doc=_SOURCE_TITLE,
            source_url=_SOURCE_URL,
            source_policy=_DOCUMENT_NUMBER,
            source_version=_VERSION,
            source_status="PENDING_CONFIRMATION",
            official_rate_book_id=book.id,
        )
        transaction.add(rate)
        transaction.flush([rate])

    return CnipaLayout246MaterializationResult(
        rate_book_id=book.id,
        rate_id=rate.id,
        disposition=CnipaLayout246MaterializationDisposition.CREATED,
    )
