from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

DeadlineSource = Literal["MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"]
DeadlineWriteStatus = Literal["CONFIRMED", "NEEDS_CONFIRMATION"]
DeadlineReadStatus = Literal["CONFIRMED", "NEEDS_CONFIRMATION", "LEGACY_UNVERIFIED"]

_DEADLINE_SOURCES = frozenset({"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"})
_DEADLINE_WRITE_STATUSES = frozenset({"CONFIRMED", "NEEDS_CONFIRMATION"})


class DocumentExtraDataError(ValueError):
    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason


class DocumentExtraDataShapeError(DocumentExtraDataError):
    pass


class DocumentExtraDataBusinessError(DocumentExtraDataError):
    pass


class _UnsetType:
    __slots__ = ()


_UNSET = _UnsetType()


@dataclass(frozen=True, slots=True)
class ParsedDocumentExtraData:
    fields: dict[str, Any]
    official_due_date: date | None
    official_due_date_source: DeadlineSource | None
    official_due_date_status: DeadlineReadStatus | None
    description: str | None
    was_legacy_text: bool


def _parse_date(value: object) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise DocumentExtraDataShapeError("OfficialDueDate", "must be an ISO date string or null")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise DocumentExtraDataShapeError(
            "OfficialDueDate", "must be an ISO date string or null"
        ) from exc
    if parsed.isoformat() != value:
        raise DocumentExtraDataShapeError("OfficialDueDate", "must use YYYY-MM-DD format")
    return parsed


def _parse_optional_code(
    fields: dict[str, Any],
    key: str,
    allowed: frozenset[str],
) -> str | None:
    value = fields.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or value not in allowed:
        raise DocumentExtraDataShapeError(key, f"must be one of {sorted(allowed)} or null")
    return value


def parse_document_extra_data(raw: str | None) -> ParsedDocumentExtraData:
    if raw is None:
        fields: dict[str, Any] = {}
        was_legacy_text = False
    elif not isinstance(raw, str):
        raise DocumentExtraDataShapeError("extra_data", "must be JSON text, plain text, or null")
    else:
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict):
            fields = dict(loaded)
            was_legacy_text = False
        else:
            fields = {"description": raw}
            was_legacy_text = True

    description = fields.get("description")
    if description is not None and not isinstance(description, str):
        raise DocumentExtraDataShapeError("description", "must be a string or null")

    official_due_date = _parse_date(fields.get("OfficialDueDate"))
    official_due_date_source = _parse_optional_code(
        fields, "OfficialDueDateSource", _DEADLINE_SOURCES
    )
    stored_status = _parse_optional_code(fields, "OfficialDueDateStatus", _DEADLINE_WRITE_STATUSES)

    if official_due_date is None:
        if official_due_date_source is not None or stored_status is not None:
            raise DocumentExtraDataBusinessError(
                "OfficialDueDate", "source and status require an official due date"
            )
        read_status: DeadlineReadStatus | None = None
    elif official_due_date_source is None and stored_status is None:
        read_status = "LEGACY_UNVERIFIED"
    elif official_due_date_source is None or stored_status is None:
        raise DocumentExtraDataBusinessError(
            "OfficialDueDate", "date, source, and status must be provided together"
        )
    else:
        read_status = stored_status

    return ParsedDocumentExtraData(
        fields=fields,
        official_due_date=official_due_date,
        official_due_date_source=official_due_date_source,
        official_due_date_status=read_status,
        description=description,
        was_legacy_text=was_legacy_text,
    )


def merge_document_extra_data(
    raw: str | None,
    *,
    official_due_date: date | None | _UnsetType = _UNSET,
    official_due_date_source: DeadlineSource | None | _UnsetType = _UNSET,
    official_due_date_status: DeadlineWriteStatus | None | _UnsetType = _UNSET,
    description: str | None | _UnsetType = _UNSET,
) -> str:
    parsed = parse_document_extra_data(raw)
    fields = dict(parsed.fields)

    if official_due_date is not _UNSET:
        if official_due_date is not None and not isinstance(official_due_date, date):
            raise DocumentExtraDataShapeError("OfficialDueDate", "must be a date value or null")
        fields["OfficialDueDate"] = (
            official_due_date.isoformat() if official_due_date is not None else None
        )
    if official_due_date_source is not _UNSET:
        fields["OfficialDueDateSource"] = official_due_date_source
    if official_due_date_status is not _UNSET:
        fields["OfficialDueDateStatus"] = official_due_date_status
    if description is not _UNSET:
        fields["description"] = description

    serialized = json.dumps(
        fields,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    merged = parse_document_extra_data(serialized)
    deadline_was_updated = any(
        value is not _UNSET
        for value in (
            official_due_date,
            official_due_date_source,
            official_due_date_status,
        )
    )
    if deadline_was_updated and merged.official_due_date_status == "LEGACY_UNVERIFIED":
        raise DocumentExtraDataBusinessError(
            "OfficialDueDate", "writes require date, source, and write status together"
        )
    return serialized
