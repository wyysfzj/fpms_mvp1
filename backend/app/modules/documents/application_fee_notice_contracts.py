from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

__all__ = (
    "ApplicationFeeNoticeItem",
    "ApplicationFeeNoticeEvidence",
    "ApplicationFeeNoticePct",
    "ApplicationFeeNotice",
    "ApplicationFeeNoticeSource",
    "ApplicationFeeNoticeSourceError",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationFeeNoticeItem:
    fee_code: str
    fee_name: str
    source_amount: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationFeeNoticeEvidence:
    evidence_version_id: str
    source_document_id: str
    content_hash: str
    lineage_key: str
    issuer: str
    document_type: str
    issued_on: date
    role: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationFeeNoticePct:
    national_stage_entry_date: date
    evidence: tuple[ApplicationFeeNoticeEvidence, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationFeeNotice:
    schema: str
    currency: str
    total_amount: Decimal
    items: tuple[ApplicationFeeNoticeItem, ...]
    pct: ApplicationFeeNoticePct | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationFeeNoticeSource:
    document_id: str
    case_id: str
    source_date: date
    due_date: date
    due_date_source: str
    due_date_status: str
    notice: ApplicationFeeNotice
    canonical_bytes: bytes
    canonical_sha256: str


class ApplicationFeeNoticeSourceError(ValueError):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        details: dict[str, str],
    ) -> None:
        self._status_code = status_code
        self._code = code
        self._details = dict(details)
        super().__init__(code)

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def code(self) -> str:
        return self._code

    @property
    def details(self) -> dict[str, str]:
        return dict(self._details)
