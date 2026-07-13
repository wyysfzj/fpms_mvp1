from __future__ import annotations

import json
from datetime import date

import pytest

from app.modules.documents.extra_data import (
    DocumentExtraDataBusinessError,
    DocumentExtraDataShapeError,
    merge_document_extra_data,
    parse_document_extra_data,
)


def test_parser_preserves_unknown_json_and_projects_legacy_due_date() -> None:
    raw_fields = {
        "OfficialDueDate": "2026-09-30",
        "description": "官文中的既有说明",
        "unknown_scalar": 17,
        "unknown_nested": {"keep": ["all", "values"]},
    }

    parsed = parse_document_extra_data(json.dumps(raw_fields, ensure_ascii=False))

    assert parsed.fields == raw_fields
    assert parsed.official_due_date == date(2026, 9, 30)
    assert parsed.official_due_date_source is None
    assert parsed.official_due_date_status == "LEGACY_UNVERIFIED"
    assert parsed.description == "官文中的既有说明"
    assert parsed.was_legacy_text is False


def test_parser_preserves_legacy_plain_text_as_description() -> None:
    parsed = parse_document_extra_data("  历史纯文本说明  ")

    assert parsed.fields == {"description": "  历史纯文本说明  "}
    assert parsed.official_due_date is None
    assert parsed.official_due_date_source is None
    assert parsed.official_due_date_status is None
    assert parsed.description == "  历史纯文本说明  "
    assert parsed.was_legacy_text is True


@pytest.mark.parametrize("raw", ["[]", '"JSON string"', "42", "null"])
def test_valid_non_object_json_remains_exact_legacy_description(raw: str) -> None:
    parsed = parse_document_extra_data(raw)

    assert parsed.fields == {"description": raw}
    assert parsed.description == raw
    assert parsed.was_legacy_text is True


def test_merger_preserves_unknown_json_while_writing_canonical_deadline() -> None:
    raw = json.dumps(
        {
            "description": "旧说明",
            "unknown_scalar": 17,
            "unknown_nested": {"keep": ["all", "values"]},
        },
        ensure_ascii=False,
    )

    merged = merge_document_extra_data(
        raw,
        official_due_date=date(2026, 10, 8),
        official_due_date_source="MANUAL_OFFICIAL_NOTICE",
        official_due_date_status="CONFIRMED",
        description="新说明",
    )

    assert merged == (
        '{"OfficialDueDate":"2026-10-08",'
        '"OfficialDueDateSource":"MANUAL_OFFICIAL_NOTICE",'
        '"OfficialDueDateStatus":"CONFIRMED",'
        '"description":"新说明",'
        '"unknown_nested":{"keep":["all","values"]},'
        '"unknown_scalar":17}'
    )
    assert json.loads(merged) == {
        "OfficialDueDate": "2026-10-08",
        "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
        "OfficialDueDateStatus": "CONFIRMED",
        "description": "新说明",
        "unknown_scalar": 17,
        "unknown_nested": {"keep": ["all", "values"]},
    }


def test_merger_converts_legacy_text_without_losing_description() -> None:
    merged = merge_document_extra_data(
        "历史纯文本说明",
        official_due_date=date(2026, 11, 12),
        official_due_date_source="IMPORTED_OFFICIAL_NOTICE",
        official_due_date_status="NEEDS_CONFIRMATION",
    )

    assert json.loads(merged) == {
        "OfficialDueDate": "2026-11-12",
        "OfficialDueDateSource": "IMPORTED_OFFICIAL_NOTICE",
        "OfficialDueDateStatus": "NEEDS_CONFIRMATION",
        "description": "历史纯文本说明",
    }


@pytest.mark.parametrize(
    ("fields", "expected_field"),
    [
        ({"OfficialDueDate": "2026-99-99"}, "OfficialDueDate"),
        ({"OfficialDueDate": 20260930}, "OfficialDueDate"),
        ({"OfficialDueDate": "20260930"}, "OfficialDueDate"),
        ({"OfficialDueDateSource": "GUESSED"}, "OfficialDueDateSource"),
        ({"OfficialDueDateStatus": "LEGACY_UNVERIFIED"}, "OfficialDueDateStatus"),
        ({"description": ["not", "text"]}, "description"),
    ],
)
def test_parser_reports_stable_shape_errors(fields: dict[str, object], expected_field: str) -> None:
    with pytest.raises(DocumentExtraDataShapeError) as exc_info:
        parse_document_extra_data(json.dumps(fields))

    assert exc_info.value.field == expected_field
    assert exc_info.value.reason


@pytest.mark.parametrize(
    "fields",
    [
        {"OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE"},
        {"OfficialDueDateStatus": "CONFIRMED"},
        {
            "OfficialDueDate": "2026-09-30",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
        },
        {
            "OfficialDueDate": "2026-09-30",
            "OfficialDueDateStatus": "CONFIRMED",
        },
    ],
)
def test_parser_separates_cross_field_business_errors(fields: dict[str, object]) -> None:
    with pytest.raises(DocumentExtraDataBusinessError) as exc_info:
        parse_document_extra_data(json.dumps(fields))

    assert exc_info.value.field == "OfficialDueDate"
    assert exc_info.value.reason


def test_merger_cannot_create_service_only_legacy_status() -> None:
    with pytest.raises(DocumentExtraDataShapeError) as exc_info:
        merge_document_extra_data(
            None,
            official_due_date=date(2026, 9, 30),
            official_due_date_source="MANUAL_OFFICIAL_NOTICE",
            official_due_date_status="LEGACY_UNVERIFIED",  # type: ignore[arg-type]
        )

    assert exc_info.value.field == "OfficialDueDateStatus"


def test_merger_rejects_new_due_date_without_source_and_write_status() -> None:
    with pytest.raises(DocumentExtraDataBusinessError) as exc_info:
        merge_document_extra_data(None, official_due_date=date(2026, 9, 30))

    assert exc_info.value.field == "OfficialDueDate"


def test_description_only_merge_preserves_existing_legacy_deadline_and_unknown_keys() -> None:
    raw = json.dumps(
        {
            "OfficialDueDate": "2026-09-30",
            "description": "旧说明",
            "unknown": {"keep": True},
        },
        ensure_ascii=False,
    )

    merged = merge_document_extra_data(raw, description="新说明")
    parsed = parse_document_extra_data(merged)

    assert parsed.official_due_date == date(2026, 9, 30)
    assert parsed.official_due_date_status == "LEGACY_UNVERIFIED"
    assert parsed.description == "新说明"
    assert parsed.fields["unknown"] == {"keep": True}


def test_omitted_deadline_fields_preserve_tuple_while_explicit_null_clears_it() -> None:
    raw = json.dumps(
        {
            "OfficialDueDate": "2026-12-31",
            "OfficialDueDateSource": "MANUAL_OFFICIAL_NOTICE",
            "OfficialDueDateStatus": "CONFIRMED",
            "description": "原说明",
            "unknown": "保留",
        },
        ensure_ascii=False,
    )

    omitted = parse_document_extra_data(merge_document_extra_data(raw, description="仅修改说明"))
    assert omitted.official_due_date == date(2026, 12, 31)
    assert omitted.official_due_date_source == "MANUAL_OFFICIAL_NOTICE"
    assert omitted.official_due_date_status == "CONFIRMED"

    cleared_raw = merge_document_extra_data(
        raw,
        official_due_date=None,
        official_due_date_source=None,
        official_due_date_status=None,
    )
    cleared = parse_document_extra_data(cleared_raw)
    assert cleared.official_due_date is None
    assert cleared.official_due_date_source is None
    assert cleared.official_due_date_status is None
    assert cleared.fields == {
        "OfficialDueDate": None,
        "OfficialDueDateSource": None,
        "OfficialDueDateStatus": None,
        "description": "原说明",
        "unknown": "保留",
    }
