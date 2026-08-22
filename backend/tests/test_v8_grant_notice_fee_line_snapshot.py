from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from typing import get_type_hints

import pytest

from app.modules.documents.extra_data import (
    DocumentExtraDataBusinessError,
    DocumentExtraDataShapeError,
)
from app.modules.documents.models import Document

DOCUMENT_ID = "document-grant-notice"
EVIDENCE_VERSION_ID = "evidence-version-1"
EVIDENCE_HASH = f"sha256:{'a' * 64}"


def _document(lines: object, **siblings: object) -> Document:
    return Document(
        id=DOCUMENT_ID,
        case_id="case-1",
        extra_data=json.dumps(
            {**siblings, "GrantFeeLines": lines},
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )


def _extract(document: Document):
    from app.modules.documents.grant_fee_lines import (
        extract_grant_notice_fee_line_snapshot,
    )

    return extract_grant_notice_fee_line_snapshot(
        document=document,
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        expected_evidence_content_hash=EVIDENCE_HASH,
    )


def _valid_line(**overrides: object) -> dict[str, object]:
    return {
        "fee_name": "授权当年年费",
        "year": 1,
        "amount": "900",
        "reduction_ratio": "0.85",
        **overrides,
    }


def test_public_contract_is_exact_frozen_and_keyword_only() -> None:
    from app.modules.documents import grant_fee_lines
    from app.modules.documents.grant_fee_lines import (
        GrantNoticeFeeLine,
        GrantNoticeFeeLineSnapshot,
        extract_grant_notice_fee_line_snapshot,
    )

    assert grant_fee_lines.__all__ == (
        "GrantNoticeFeeLine",
        "GrantNoticeFeeLineSnapshot",
        "extract_grant_notice_fee_line_snapshot",
    )
    assert list(get_type_hints(GrantNoticeFeeLine).items()) == [
        ("fee_name", str),
        ("year", int),
        ("amount", Decimal),
        ("reduction_ratio", Decimal),
    ]
    assert list(get_type_hints(GrantNoticeFeeLineSnapshot).items()) == [
        ("schema", str),
        ("source_document_id", str),
        ("reviewed_evidence_version_id", str),
        ("reviewed_evidence_content_hash", str),
        ("lines", tuple[GrantNoticeFeeLine, ...]),
        ("canonical_json", str),
        ("snapshot_hash", str),
    ]
    assert [field.name for field in fields(GrantNoticeFeeLine)] == [
        "fee_name",
        "year",
        "amount",
        "reduction_ratio",
    ]
    assert [field.name for field in fields(GrantNoticeFeeLineSnapshot)] == [
        "schema",
        "source_document_id",
        "reviewed_evidence_version_id",
        "reviewed_evidence_content_hash",
        "lines",
        "canonical_json",
        "snapshot_hash",
    ]
    assert "__slots__" in GrantNoticeFeeLine.__dict__
    assert "__slots__" in GrantNoticeFeeLineSnapshot.__dict__
    assert GrantNoticeFeeLine.__dataclass_params__.frozen is True
    assert GrantNoticeFeeLineSnapshot.__dataclass_params__.frozen is True
    with pytest.raises(TypeError):
        GrantNoticeFeeLine("fee", 1, Decimal("1"), Decimal("0"))  # type: ignore[misc]

    signature = inspect.signature(extract_grant_notice_fee_line_snapshot)
    assert list(signature.parameters) == [
        "document",
        "reviewed_evidence_version_id",
        "expected_evidence_content_hash",
    ]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )


def test_valid_snapshot_preserves_order_and_exact_provenance() -> None:
    lines = [
        _valid_line(),
        _valid_line(
            fee_name="授权第二年年费",
            year=2,
            amount="1200.0",
            reduction_ratio="0.7",
        ),
    ]
    document = _document(lines, unrelated={"kept_out": True})
    original_extra_data = document.extra_data
    original_state = dict(document.__dict__)

    result = _extract(document)

    assert result.schema == "FPMS_GRANT_NOTICE_FEE_LINES_V1"
    assert result.source_document_id == DOCUMENT_ID
    assert result.reviewed_evidence_version_id == EVIDENCE_VERSION_ID
    assert result.reviewed_evidence_content_hash == EVIDENCE_HASH
    assert [(line.fee_name, line.year) for line in result.lines] == [
        ("授权当年年费", 1),
        ("授权第二年年费", 2),
    ]
    assert result.lines[0].amount == Decimal("900.00")
    assert result.lines[0].reduction_ratio == Decimal("0.85")
    expected_payload = {
        "schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
        "source_document_id": DOCUMENT_ID,
        "reviewed_evidence_version_id": EVIDENCE_VERSION_ID,
        "reviewed_evidence_content_hash": EVIDENCE_HASH,
        "lines": [
            {
                "fee_name": "授权当年年费",
                "year": 1,
                "amount": "900.00",
                "reduction_ratio": "0.85",
            },
            {
                "fee_name": "授权第二年年费",
                "year": 2,
                "amount": "1200.00",
                "reduction_ratio": "0.7",
            },
        ],
    }
    expected_json = json.dumps(
        expected_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert result.canonical_json == expected_json
    assert result.snapshot_hash == hashlib.sha256(expected_json.encode()).hexdigest()
    assert document.extra_data == original_extra_data
    assert document.__dict__ == original_state
    with pytest.raises(FrozenInstanceError):
        result.schema = "changed"  # type: ignore[misc]


def test_equivalent_amount_spellings_canonicalize_identically() -> None:
    results = [
        _extract(_document([_valid_line(amount=value)])) for value in ("900", "900.0", "900.00")
    ]
    assert {result.canonical_json for result in results} == {results[0].canonical_json}
    assert {result.snapshot_hash for result in results} == {results[0].snapshot_hash}


def test_arbitrarily_long_valid_plain_decimal_remains_canonical() -> None:
    amount = "12345678901234567890123456789.00"
    result = _extract(_document([_valid_line(amount=amount)]))
    assert result.lines[0].amount == Decimal(amount)
    assert json.loads(result.canonical_json)["lines"][0]["amount"] == amount


@pytest.mark.parametrize(
    ("raw", "field"),
    [
        (None, "extra_data"),
        ("null", "extra_data"),
        ("[]", "extra_data"),
        ("{", "extra_data"),
        ("{}", "GrantFeeLines"),
        ('{"GrantFeeLines":null}', "GrantFeeLines"),
        ('{"GrantFeeLines":{}}', "GrantFeeLines"),
        ('{"GrantFeeLines":[]}', "GrantFeeLines"),
        ('{"GrantFeeLines":[],"GrantFeeLines":[]}', "extra_data"),
        (
            '{"GrantFeeLines":[{"fee_name":"a","fee_name":"b","year":1,"amount":"1","reduction_ratio":"0"}]}',
            "GrantFeeLines[0].fee_name",
        ),
        ('{"GrantFeeLines":[NaN]}', "extra_data"),
    ],
)
def test_json_and_container_shape_failures_are_strict(raw: str | None, field: str) -> None:
    document = Document(id=DOCUMENT_ID, case_id="case-1", extra_data=raw)
    with pytest.raises(DocumentExtraDataShapeError) as exc_info:
        _extract(document)
    assert exc_info.value.field == field


@pytest.mark.parametrize(
    ("line", "field"),
    [
        ("not-an-object", "GrantFeeLines[0]"),
        ({"fee_name": "a"}, "GrantFeeLines[0]"),
        ({**_valid_line(), "extra": "x"}, "GrantFeeLines[0]"),
        (_valid_line(fee_name=1), "GrantFeeLines[0].fee_name"),
        (_valid_line(year=True), "GrantFeeLines[0].year"),
        (_valid_line(amount=900), "GrantFeeLines[0].amount"),
        (_valid_line(reduction_ratio=0.85), "GrantFeeLines[0].reduction_ratio"),
    ],
)
def test_line_shape_and_wrong_json_types_are_rejected(line: object, field: str) -> None:
    with pytest.raises(DocumentExtraDataShapeError) as exc_info:
        _extract(_document([line]))
    assert exc_info.value.field == field


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"fee_name": ""}, "GrantFeeLines[0].fee_name"),
        ({"fee_name": " fee"}, "GrantFeeLines[0].fee_name"),
        ({"fee_name": "fee\x00"}, "GrantFeeLines[0].fee_name"),
        ({"year": 0}, "GrantFeeLines[0].year"),
        ({"year": -1}, "GrantFeeLines[0].year"),
        ({"amount": "0"}, "GrantFeeLines[0].amount"),
        ({"amount": "-1"}, "GrantFeeLines[0].amount"),
        ({"amount": "+1"}, "GrantFeeLines[0].amount"),
        ({"amount": "1e3"}, "GrantFeeLines[0].amount"),
        ({"amount": " 1"}, "GrantFeeLines[0].amount"),
        ({"amount": "1.001"}, "GrantFeeLines[0].amount"),
        ({"reduction_ratio": "0.70"}, "GrantFeeLines[0].reduction_ratio"),
        ({"reduction_ratio": "1"}, "GrantFeeLines[0].reduction_ratio"),
    ],
)
def test_line_business_rules_fail_closed(overrides: dict[str, object], field: str) -> None:
    with pytest.raises(DocumentExtraDataBusinessError) as exc_info:
        _extract(_document([_valid_line(**overrides)]))
    assert exc_info.value.field == field


def test_duplicate_year_is_rejected_in_array_order() -> None:
    with pytest.raises(DocumentExtraDataBusinessError) as exc_info:
        _extract(_document([_valid_line(), _valid_line(year=1, fee_name="another")]))
    assert exc_info.value.field == "GrantFeeLines[1].year"


@pytest.mark.parametrize(
    ("document", "version_id", "content_hash", "error_type", "field"),
    [
        (object(), EVIDENCE_VERSION_ID, EVIDENCE_HASH, DocumentExtraDataShapeError, "document"),
        (
            Document(id="", case_id="case-1"),
            EVIDENCE_VERSION_ID,
            EVIDENCE_HASH,
            DocumentExtraDataBusinessError,
            "document.id",
        ),
        (
            Document(id="x" * 37, case_id="case-1"),
            EVIDENCE_VERSION_ID,
            EVIDENCE_HASH,
            DocumentExtraDataBusinessError,
            "document.id",
        ),
        (
            _document([_valid_line()]),
            " ",
            EVIDENCE_HASH,
            DocumentExtraDataBusinessError,
            "reviewed_evidence_version_id",
        ),
        (
            _document([_valid_line()]),
            "x" * 37,
            EVIDENCE_HASH,
            DocumentExtraDataBusinessError,
            "reviewed_evidence_version_id",
        ),
        (
            _document([_valid_line()]),
            EVIDENCE_VERSION_ID,
            "a" * 64,
            DocumentExtraDataBusinessError,
            "expected_evidence_content_hash",
        ),
        (
            _document([_valid_line()]),
            EVIDENCE_VERSION_ID,
            f"sha256:{'A' * 64}",
            DocumentExtraDataBusinessError,
            "expected_evidence_content_hash",
        ),
        (
            _document([_valid_line()]),
            EVIDENCE_VERSION_ID,
            f" sha256:{'a' * 64}",
            DocumentExtraDataBusinessError,
            "expected_evidence_content_hash",
        ),
    ],
)
def test_binding_validation_precedes_line_parsing(
    document: object,
    version_id: str,
    content_hash: str,
    error_type: type[ValueError],
    field: str,
) -> None:
    from app.modules.documents.grant_fee_lines import extract_grant_notice_fee_line_snapshot

    if isinstance(document, Document):
        document.extra_data = '{"GrantFeeLines":[null]}'
    with pytest.raises(error_type) as exc_info:
        extract_grant_notice_fee_line_snapshot(
            document=document,  # type: ignore[arg-type]
            reviewed_evidence_version_id=version_id,
            expected_evidence_content_hash=content_hash,
        )
    assert exc_info.value.field == field


def test_unrelated_siblings_do_not_change_snapshot_but_bound_facts_do() -> None:
    from app.modules.documents.grant_fee_lines import extract_grant_notice_fee_line_snapshot

    base = _extract(_document([_valid_line()]))
    with_sibling = _extract(_document([_valid_line()], other={"ignored": 1}))
    changed_order = _extract(
        _document([_valid_line(year=2), _valid_line(year=1, fee_name="second")])
    )
    changed_document = _document([_valid_line()])
    changed_document.id = "different-document"
    changed_document_snapshot = _extract(changed_document)
    changed_version = extract_grant_notice_fee_line_snapshot(
        document=_document([_valid_line()]),
        reviewed_evidence_version_id="different-version",
        expected_evidence_content_hash=EVIDENCE_HASH,
    )
    changed_hash = extract_grant_notice_fee_line_snapshot(
        document=_document([_valid_line()]),
        reviewed_evidence_version_id=EVIDENCE_VERSION_ID,
        expected_evidence_content_hash=f"sha256:{'b' * 64}",
    )
    assert with_sibling == base
    assert {
        changed_order.snapshot_hash,
        changed_document_snapshot.snapshot_hash,
        changed_version.snapshot_hash,
        changed_hash.snapshot_hash,
    }.isdisjoint({base.snapshot_hash})


def test_spies_prove_no_sql_io_clock_or_business_side_effects(engine, monkeypatch) -> None:
    import builtins
    import time
    from pathlib import Path

    from sqlalchemy import event
    from sqlalchemy.orm import Session

    from app.modules.cases import lifecycle_activity_service
    from app.modules.documents import fee_linking_service
    from app.modules.fees import fee_reduction, obligation_service
    from app.modules.fees import service as fee_service
    from app.modules.tasks import service as task_service

    calls: list[str] = []

    def forbidden(name: str):
        def fail(*_args: object, **_kwargs: object) -> None:
            calls.append(name)
            raise AssertionError(f"unexpected side effect: {name}")

        return fail

    def before_cursor_execute(*_args: object, **_kwargs: object) -> None:
        calls.append("sql")
        raise AssertionError("unexpected SQL")

    document = _document([_valid_line()])
    original_state = dict(document.__dict__)
    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        with monkeypatch.context() as spies:
            spies.setattr(builtins, "open", forbidden("file"))
            spies.setattr(Path, "open", forbidden("path"))
            spies.setattr(time, "time", forbidden("clock"))
            spies.setattr(Session, "execute", forbidden("session.execute"))
            spies.setattr(Session, "add", forbidden("session.add"))
            spies.setattr(Session, "flush", forbidden("session.flush"))
            spies.setattr(
                lifecycle_activity_service,
                "append_case_activity",
                forbidden("activity"),
            )
            spies.setattr(
                fee_reduction,
                "validate_fee_reduction",
                forbidden("eligibility"),
            )
            spies.setattr(obligation_service, "preview_estimate", forbidden("rate"))
            spies.setattr(
                obligation_service,
                "recognize_obligation",
                forbidden("obligation"),
            )
            spies.setattr(fee_service, "create_fee_draft", forbidden("draft"))
            spies.setattr(task_service, "create_task", forbidden("task"))
            spies.setattr(
                fee_linking_service,
                "maybe_create_fee_draft",
                forbidden("document-draft"),
            )

            result = _extract(document)
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

    assert result.source_document_id == DOCUMENT_ID
    assert document.__dict__ == original_state
    assert calls == []
