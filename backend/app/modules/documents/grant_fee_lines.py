from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal

from app.modules.documents.extra_data import (
    DocumentExtraDataBusinessError,
    DocumentExtraDataShapeError,
)
from app.modules.documents.models import Document

__all__ = (
    "GrantNoticeFeeLine",
    "GrantNoticeFeeLineSnapshot",
    "extract_grant_notice_fee_line_snapshot",
)

_SCHEMA = "FPMS_GRANT_NOTICE_FEE_LINES_V1"
_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_AMOUNT_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]{1,2})?")
_LINE_FIELDS = frozenset({"fee_name", "year", "amount", "reduction_ratio"})
_RATIOS = {"0": Decimal("0"), "0.7": Decimal("0.7"), "0.85": Decimal("0.85")}


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantNoticeFeeLine:
    fee_name: str
    year: int
    amount: Decimal
    reduction_ratio: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantNoticeFeeLineSnapshot:
    schema: str
    source_document_id: str
    reviewed_evidence_version_id: str
    reviewed_evidence_content_hash: str
    lines: tuple[GrantNoticeFeeLine, ...]
    canonical_json: str
    snapshot_hash: str


def _reject_constant(value: str) -> object:
    raise DocumentExtraDataShapeError("extra_data", f"non-finite token {value!r} is not allowed")


class _JsonObjectPairs(list[tuple[str, object]]):
    pass


def _materialize_json(value: object, path: str) -> object:
    if isinstance(value, _JsonObjectPairs):
        result: dict[str, object] = {}
        for key, child in value:
            if key in result:
                field = f"{path}.{key}" if path.startswith("GrantFeeLines[") else "extra_data"
                raise DocumentExtraDataShapeError(field, "duplicate object keys are not allowed")
            child_path = (
                "GrantFeeLines"
                if path == "extra_data" and key == "GrantFeeLines"
                else f"{path}.{key}"
                if path.startswith("GrantFeeLines")
                else "extra_data"
            )
            result[key] = _materialize_json(child, child_path)
        return result
    if isinstance(value, list):
        return [_materialize_json(child, f"{path}[{index}]") for index, child in enumerate(value)]
    return value


def _require_bound_id(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise DocumentExtraDataShapeError(field, "must be a string")
    if not value.strip() or len(value) > 36:
        raise DocumentExtraDataBusinessError(field, "must be nonblank and at most 36 characters")
    return value


def _parse_extra_data(raw: object) -> dict[str, object]:
    if not isinstance(raw, str):
        raise DocumentExtraDataShapeError("extra_data", "must be JSON text")
    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=_JsonObjectPairs,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise DocumentExtraDataShapeError("extra_data", "must be valid JSON") from exc
    parsed = _materialize_json(parsed, "extra_data")
    if not isinstance(parsed, dict):
        raise DocumentExtraDataShapeError("extra_data", "root must be an object")
    if "GrantFeeLines" not in parsed:
        raise DocumentExtraDataShapeError("GrantFeeLines", "is required")
    return parsed


def _parse_line(item: object, index: int, seen_years: set[int]) -> GrantNoticeFeeLine:
    prefix = f"GrantFeeLines[{index}]"
    if not isinstance(item, dict):
        raise DocumentExtraDataShapeError(prefix, "must be an object")
    if set(item) != _LINE_FIELDS:
        raise DocumentExtraDataShapeError(prefix, "must contain exactly the frozen line fields")

    fee_name = item["fee_name"]
    if not isinstance(fee_name, str):
        raise DocumentExtraDataShapeError(f"{prefix}.fee_name", "must be a string")
    if not fee_name or fee_name != fee_name.strip() or "\x00" in fee_name:
        raise DocumentExtraDataBusinessError(
            f"{prefix}.fee_name", "must be nonblank, trimmed and contain no NUL"
        )

    year = item["year"]
    if type(year) is not int:
        raise DocumentExtraDataShapeError(f"{prefix}.year", "must be an integer")
    if year <= 0:
        raise DocumentExtraDataBusinessError(f"{prefix}.year", "must be greater than zero")
    if year in seen_years:
        raise DocumentExtraDataBusinessError(f"{prefix}.year", "must be unique")
    seen_years.add(year)

    amount_text = item["amount"]
    if not isinstance(amount_text, str):
        raise DocumentExtraDataShapeError(f"{prefix}.amount", "must be a decimal string")
    if _AMOUNT_PATTERN.fullmatch(amount_text) is None:
        raise DocumentExtraDataBusinessError(
            f"{prefix}.amount", "must be an unsigned plain decimal with at most two places"
        )
    amount = Decimal(amount_text)
    if not amount.is_finite() or amount <= 0:
        raise DocumentExtraDataBusinessError(f"{prefix}.amount", "must be finite and positive")

    ratio_text = item["reduction_ratio"]
    if not isinstance(ratio_text, str):
        raise DocumentExtraDataShapeError(f"{prefix}.reduction_ratio", "must be a decimal string")
    if ratio_text not in _RATIOS:
        raise DocumentExtraDataBusinessError(
            f"{prefix}.reduction_ratio", "must be exactly 0, 0.7 or 0.85"
        )

    canonical_amount = Decimal(format(amount, ".2f"))
    return GrantNoticeFeeLine(
        fee_name=fee_name,
        year=year,
        amount=canonical_amount,
        reduction_ratio=_RATIOS[ratio_text],
    )


def extract_grant_notice_fee_line_snapshot(
    *,
    document: Document,
    reviewed_evidence_version_id: str,
    expected_evidence_content_hash: str,
) -> GrantNoticeFeeLineSnapshot:
    if not isinstance(document, Document):
        raise DocumentExtraDataShapeError("document", "must be a Document")
    document_id = _require_bound_id(document.id, "document.id")
    evidence_version_id = _require_bound_id(
        reviewed_evidence_version_id, "reviewed_evidence_version_id"
    )
    if not isinstance(expected_evidence_content_hash, str):
        raise DocumentExtraDataShapeError("expected_evidence_content_hash", "must be a string")
    if _HASH_PATTERN.fullmatch(expected_evidence_content_hash) is None:
        raise DocumentExtraDataBusinessError(
            "expected_evidence_content_hash", "must be an exact lowercase sha256 value"
        )

    extra_data = _parse_extra_data(document.extra_data)
    raw_lines = extra_data["GrantFeeLines"]
    if not isinstance(raw_lines, list):
        raise DocumentExtraDataShapeError("GrantFeeLines", "must be an array")
    if not raw_lines:
        raise DocumentExtraDataShapeError("GrantFeeLines", "must be nonempty")

    seen_years: set[int] = set()
    lines = tuple(_parse_line(item, index, seen_years) for index, item in enumerate(raw_lines))
    payload = {
        "schema": _SCHEMA,
        "source_document_id": document_id,
        "reviewed_evidence_version_id": evidence_version_id,
        "reviewed_evidence_content_hash": expected_evidence_content_hash,
        "lines": [
            {
                "fee_name": line.fee_name,
                "year": line.year,
                "amount": format(line.amount, ".2f"),
                "reduction_ratio": str(line.reduction_ratio),
            }
            for line in lines
        ],
    }
    canonical_json = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return GrantNoticeFeeLineSnapshot(
        schema=_SCHEMA,
        source_document_id=document_id,
        reviewed_evidence_version_id=evidence_version_id,
        reviewed_evidence_content_hash=expected_evidence_content_hash,
        lines=lines,
        canonical_json=canonical_json,
        snapshot_hash=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )
