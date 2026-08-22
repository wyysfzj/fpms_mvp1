from __future__ import annotations

import hashlib
import inspect
import json
import socket
import sys
import urllib.request
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import get_type_hints
from uuid import uuid4

import pytest
from sqlalchemy import event, select, text
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker

import app.modules.fees.models as fee_models_module
import app.modules.fees.obligation_service as obligation_service_module
import app.modules.fees.official_rate_book as official_rate_book_module
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.documents.models import DocAttachment, Document, DocumentEvidenceVersion
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInputProvenance,
)
from app.modules.fees.models import FeeRate, FeeReductionApproval, OfficialRateBook
from app.modules.fees.obligation_contracts import (
    FeeEstimateContext,
    FeeSourceStatus,
    PreviewFeeEstimateCommand,
)
from app.modules.fees.obligation_service import (
    FeeEstimatePreviewError,
    FeeEstimatePreviewErrorCode,
    OfficialFeeEstimateRateCandidate,
    OfficialFeeEstimateRateProvider,
    preview_estimate,
)
from app.modules.fees.official_rate_book import SqlAlchemyOfficialFeeEstimateRateProvider
from scripts import seed_dev

EFFECTIVE_ON = date(2026, 7, 14)
REFERENCE = "https://www.cnipa.gov.cn/art/2026/7/14/synthetic-rate-book.html"


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_snapshot(*, url: str = REFERENCE) -> tuple[str, str]:
    snapshot = _canonical(
        {
            "schema_version": "CNIPA_RATE_SOURCE_V1",
            "sources": [
                {
                    "content_sha256": "a" * 64,
                    "document_no": None,
                    "published_on": "2026-07-14",
                    "retrieved_at": "2026-07-14T00:00:00Z",
                    "title": "Synthetic CNIPA provider fixture — not a legal rate source",
                    "url": url,
                }
            ],
        }
    )
    return snapshot, _digest(snapshot)


def _admin(transaction: Session) -> T_User:
    actor = transaction.scalar(select(T_User).where(T_User.username == "admin"))
    assert actor is not None
    return actor


def _case(
    transaction: Session,
    *,
    category: str = "INV",
    trigger: str = "FILING_ACCEPTED",
    claim_count: int | None = 12,
    has_exam_request: bool | None = True,
    fee_reduction: str | None = "0",
    case_type: str = "NORMAL",
    flow_dir: str = "CN_DOMESTIC",
) -> tuple[Case, PreviewFeeEstimateCommand]:
    row = Case(
        id=str(uuid4()),
        case_no=f"PROVIDER-{uuid4()}",
        case_type=case_type,
        flow_dir=flow_dir,
        patent_category=category,
        claim_count=claim_count,
        has_exam_request=has_exam_request,
        fee_reduction=fee_reduction,
    )
    transaction.add(row)
    transaction.commit()
    return row, PreviewFeeEstimateCommand(
        case_id=row.id,
        trigger_context=FeeEstimateContext(
            trigger=trigger,
            source_document_id="DOC-SYNTHETIC-001",
        ),
        currency="CNY",
    )


def _book(
    transaction: Session,
    *,
    book_code: str = "CNIPA-PATENT-FEES",
    approval_status: str = "APPROVED",
    activation_status: str = "ACTIVE",
    effective_from: date = EFFECTIVE_ON,
    effective_to: date | None = EFFECTIVE_ON,
    source_reference: str = REFERENCE,
) -> OfficialRateBook:
    actor = _admin(transaction)
    snapshot, snapshot_hash = _source_snapshot(url=source_reference)
    active = activation_status == "ACTIVE"
    approved = approval_status == "APPROVED"
    row = OfficialRateBook(
        id=str(uuid4()),
        book_code=book_code,
        version_code=f"SYNTHETIC-{uuid4()}",
        source_authority="CNIPA",
        source_reference=source_reference,
        source_version="SYNTHETIC-CNIPA-PROVIDER-FIXTURE",
        source_published_on=EFFECTIVE_ON,
        source_snapshot=snapshot,
        source_snapshot_hash=snapshot_hash,
        approval_status=approval_status,
        approved_by=actor.id if approved else None,
        approved_at=datetime(2026, 7, 14, 8, 0) if approved else None,
        effective_from=effective_from,
        effective_to=effective_to,
        activation_status=activation_status,
        activated_by=actor.id if active else None,
        activated_at=datetime(2026, 7, 14, 9, 0) if active else None,
        current_identity_key=f"CNIPA|{book_code}" if active else None,
    )
    transaction.add(row)
    transaction.commit()
    return row


def _rate(
    transaction: Session,
    book: OfficialRateBook,
    fee_code: str,
    *,
    amount: str = "100.00",
    calc_mode: str = "FIXED",
    allow_reduction: bool | None = True,
    currency: str = "CNY",
    enabled: bool = True,
    effective_from: date = EFFECTIVE_ON,
    effective_to: date | None = EFFECTIVE_ON,
) -> FeeRate:
    row = FeeRate(
        fee_code=fee_code,
        fee_name=f"Synthetic {fee_code}",
        fee_type="GOV",
        currency=currency,
        default_amount=Decimal(amount),
        enabled=enabled,
        calc_mode=calc_mode,
        allow_reduction=allow_reduction,
        effective_from=effective_from,
        effective_to=effective_to,
        official_rate_book_id=book.id,
    )
    transaction.add(row)
    transaction.commit()
    return row


def _seed_filing_rates(transaction: Session, book: OfficialRateBook) -> dict[str, FeeRate]:
    rows = {
        code: _rate(transaction, book, code, amount=amount, calc_mode=mode)
        for code, amount, mode in (
            ("CN_INV_APPLICATION_FEE", "900.00", "FIXED"),
            ("CN_UM_APPLICATION_FEE", "500.00", "FIXED"),
            ("CN_DES_APPLICATION_FEE", "500.00", "FIXED"),
            ("CN_EXCESS_CLAIM_FEE", "150.00", "PER_CLAIM"),
            ("CN_PUBLICATION_PRINT_FEE", "50.00", "FIXED"),
            ("CN_SUBSTANTIVE_EXAM_FEE", "2500.00", "FIXED"),
        )
    }
    return rows


def _seed_reexam_rates(transaction: Session, book: OfficialRateBook) -> dict[str, FeeRate]:
    return {
        code: _rate(transaction, book, code)
        for code in ("CN_REEXAM_FEE_INV", "CN_REEXAM_FEE_UM", "CN_REEXAM_FEE_DES")
    }


def _approval(
    transaction: Session,
    case: Case,
    *,
    ratio: str,
    fee_codes: tuple[str, ...],
    status: str = "CONFIRMED",
    scope_type: str = "CASE",
    fee_year_from: int | None = None,
    fee_year_to: int | None = None,
    effective_from: date = EFFECTIVE_ON,
    effective_to: date | None = EFFECTIVE_ON,
) -> FeeReductionApproval:
    actor = _admin(transaction)
    document = Document(id=str(uuid4()), case_id=case.id)
    transaction.add(document)
    transaction.flush()
    attachment = DocAttachment(
        id=str(uuid4()),
        document_id=document.id,
        file_name="synthetic-fee-reduction.pdf",
        file_path="/synthetic/fee-reduction.pdf",
    )
    transaction.add(attachment)
    transaction.flush()
    evidence = DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=case.id,
        document_id=document.id,
        attachment_id=attachment.id,
        lineage_key=f"fee-reduction-{uuid4()}",
        role="OFFICIAL_NOTICE",
        version_number=1,
        state="FINAL",
        creator_id=actor.id,
        review_state="APPROVED",
        reviewer_id=actor.id,
        reviewed_at=datetime(2026, 7, 14, 9, 0),
        final_submitted_at=datetime(2026, 7, 14, 9, 0),
        content_hash="sha256:" + "b" * 64,
    )
    transaction.add(evidence)
    transaction.flush()
    canonical_codes = tuple(sorted(fee_codes))
    fee_snapshot = _canonical(
        {"fee_codes": canonical_codes, "schema": "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"}
    )
    eligibility_snapshot = _canonical(
        {
            "applicants": [{"applicant_id": case.id, "attributes": {"synthetic": True}}],
            "attributes_version": "synthetic-v1",
            "schema": "FPMS_FEE_REDUCTION_ELIGIBILITY_V1",
        }
    )
    row = FeeReductionApproval(
        id=str(uuid4()),
        scope_type=scope_type,
        case_id=case.id if scope_type == "CASE" else None,
        applicant_set_key=None if scope_type == "CASE" else _digest(case.id),
        reduction_ratio=Decimal(ratio),
        fee_scope_snapshot=fee_snapshot,
        fee_scope_hash=_digest(fee_snapshot),
        fee_year_from=fee_year_from,
        fee_year_to=fee_year_to,
        effective_from=effective_from,
        effective_to=effective_to,
        source_evidence_version_id=evidence.id,
        confirmation_status=status,
        confirmed_at=datetime(2026, 7, 14, 10, 0),
        confirmed_by=actor.id,
        eligibility_snapshot=eligibility_snapshot,
        eligibility_snapshot_hash=_digest(eligibility_snapshot),
        approval_identity_key=_digest(str(uuid4())),
    )
    transaction.add(row)
    transaction.commit()
    return row


def _unsafe_update(
    transaction: Session,
    table: str,
    assignment: str,
    *,
    row_id: str,
    values: dict[str, object],
    ignore_checks: bool = False,
) -> None:
    if ignore_checks:
        transaction.execute(text("PRAGMA ignore_check_constraints=ON"))
    try:
        transaction.execute(
            text(f"UPDATE {table} SET {assignment} WHERE id = :row_id"),
            {"row_id": row_id, **values},
        )
        transaction.commit()
    finally:
        if ignore_checks:
            transaction.execute(text("PRAGMA ignore_check_constraints=OFF"))
            transaction.commit()
    transaction.expire_all()


def _read_only_state(transaction: Session) -> tuple[object, ...]:
    tables = (
        "t_case",
        "t_fee_rate_book",
        "t_fee_rate",
        "t_fee_reduction_approval",
    )
    database = tuple(
        (
            table,
            tuple(transaction.execute(text(f"SELECT * FROM {table} ORDER BY id")).all()),
        )
        for table in tables
    )
    identity_keys = tuple(sorted(repr(key) for key in transaction.identity_map))
    identity_objects = tuple(
        sorted(
            (
                repr(key),
                tuple(
                    (attribute.key, getattr(instance, attribute.key))
                    for attribute in sa_inspect(instance).mapper.column_attrs
                ),
            )
            for key, instance in transaction.identity_map.items()
        )
    )
    unit_of_work = (
        tuple(sorted(repr(item) for item in transaction.new)),
        tuple(sorted(repr(item) for item in transaction.dirty)),
        tuple(sorted(repr(item) for item in transaction.deleted)),
    )
    return (
        database,
        identity_keys,
        identity_objects,
        unit_of_work,
        transaction.in_transaction(),
        transaction.in_nested_transaction(),
    )


def _error(
    provider: SqlAlchemyOfficialFeeEstimateRateProvider,
    command: PreviewFeeEstimateCommand,
    code: FeeEstimatePreviewErrorCode,
    details: dict[str, str | int | bool | None],
    *,
    effective_on: object = EFFECTIVE_ON,
) -> FeeEstimatePreviewError:
    transaction = provider._transaction
    transaction.execute(text("SELECT 1"))
    before = _read_only_state(transaction)
    with pytest.raises(FeeEstimatePreviewError) as caught:
        provider.select_rate_candidates(
            command=command,
            rate_effective_on=effective_on,  # type: ignore[arg-type]
        )
    assert caught.value.code is code
    assert caught.value.details == details
    error = caught.value
    error.__traceback__ = None
    after = _read_only_state(transaction)
    assert after == before
    return error


def test_public_contract_is_exact_synchronous_keyword_only_and_structural() -> None:
    signature = inspect.signature(SqlAlchemyOfficialFeeEstimateRateProvider)
    assert tuple(signature.parameters) == ("transaction",)
    method = inspect.signature(SqlAlchemyOfficialFeeEstimateRateProvider.select_rate_candidates)
    assert tuple(method.parameters) == ("self", "command", "rate_effective_on")
    assert method.parameters["command"].kind is inspect.Parameter.KEYWORD_ONLY
    assert method.parameters["rate_effective_on"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(SqlAlchemyOfficialFeeEstimateRateProvider.__init__) == {
        "transaction": Session,
        "return": type(None),
    }
    assert get_type_hints(SqlAlchemyOfficialFeeEstimateRateProvider.select_rate_candidates) == {
        "command": PreviewFeeEstimateCommand,
        "rate_effective_on": date,
        "return": tuple[OfficialFeeEstimateRateCandidate, ...],
    }
    assert set(OfficialFeeEstimateRateProvider.__dict__) <= {
        "__module__",
        "__doc__",
        "select_rate_candidates",
        "__dict__",
        "__weakref__",
        "__parameters__",
        "__abstractmethods__",
        "_abc_impl",
        "_is_protocol",
        "__subclasshook__",
        "__init__",
    }


def test_filing_inv_maps_exact_order_amounts_source_and_two_selects_without_writes(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case, command = _case(transaction)
        book = _book(transaction)
        rates = _seed_filing_rates(transaction, book)
        statements: list[str] = []

        def spy(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
            statements.append(statement)

        event.listen(transaction.bind, "before_cursor_execute", spy)
        try:
            before_rows = transaction.execute(
                text(
                    "SELECT id, updated_at FROM t_case UNION ALL SELECT id, updated_at FROM t_fee_rate"
                )
            ).all()
            statements.clear()
            provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
            candidates = provider.select_rate_candidates(
                command=command,
                rate_effective_on=EFFECTIVE_ON,
            )
            select_statements = [
                statement
                for statement in statements
                if statement.lstrip().upper().startswith("SELECT")
            ]
            statements.clear()
            after_rows = transaction.execute(
                text(
                    "SELECT id, updated_at FROM t_case UNION ALL SELECT id, updated_at FROM t_fee_rate"
                )
            ).all()
        finally:
            event.remove(transaction.bind, "before_cursor_execute", spy)

        assert len(select_statements) == 2
        assert before_rows == after_rows
        assert not transaction.new and not transaction.dirty and not transaction.deleted
        assert tuple(candidate.fee_code for candidate in candidates) == (
            "CN_INV_APPLICATION_FEE",
            "CN_EXCESS_CLAIM_FEE",
            "CN_PUBLICATION_PRINT_FEE",
            "CN_SUBSTANTIVE_EXAM_FEE",
        )
        assert tuple(candidate.official_full_amount for candidate in candidates) == (
            Decimal("900.00"),
            Decimal("300.00"),
            Decimal("50.00"),
            Decimal("2500.00"),
        )
        for candidate in candidates:
            rate = rates[candidate.fee_code]
            assert candidate.fee_year_key == 0
            assert candidate.source.rate_id == rate.id
            assert candidate.source.source_document_id == "DOC-SYNTHETIC-001"
            assert candidate.source.source_doc == book.source_version
            assert candidate.source.source_url == book.source_reference
            assert candidate.source.source_policy == book.book_code
            assert candidate.source.source_version == book.version_code
            assert candidate.source.status is FeeSourceStatus.VERIFIED
            assert candidate.reduction_input.reduction_ratio == Decimal("0")
            assert (
                candidate.reduction_input.provenance is FeeReductionInputProvenance.EXPLICIT_ENTRY
            )
            assert candidate.reduction_context == FeeReductionEvaluationContext(
                case_id=case.id,
                applicant_set_key=None,
                fee_code=candidate.fee_code,
                fee_year_key=0,
                as_of_date=EFFECTIVE_ON,
            )
            assert candidate.reduction_approval is None

        estimate = preview_estimate(
            command=command,
            rate_effective_on=EFFECTIVE_ON,
            rate_provider=provider,
        )
        assert estimate.total_payable_amount == Decimal("3750.00")


@pytest.mark.parametrize(
    ("trigger", "category", "claim_count", "has_exam_request", "expected"),
    (
        (
            "FILING_ACCEPTED",
            "INV",
            10,
            False,
            ("CN_INV_APPLICATION_FEE", "CN_PUBLICATION_PRINT_FEE"),
        ),
        ("FILING_ACCEPTED", "UM", 10, None, ("CN_UM_APPLICATION_FEE",)),
        ("FILING_ACCEPTED", "DES", 10, None, ("CN_DES_APPLICATION_FEE",)),
        ("REEXAM_REQUESTED", "INV", None, None, ("CN_REEXAM_FEE_INV",)),
        ("REEXAM_REQUESTED", "UM", None, None, ("CN_REEXAM_FEE_UM",)),
        ("REEXAM_REQUESTED", "DES", None, None, ("CN_REEXAM_FEE_DES",)),
    ),
)
def test_exact_trigger_category_mapping(
    session_factory: sessionmaker,
    trigger: str,
    category: str,
    claim_count: int | None,
    has_exam_request: bool | None,
    expected: tuple[str, ...],
) -> None:
    with session_factory() as transaction:
        _, command = _case(
            transaction,
            trigger=trigger,
            category=category,
            claim_count=claim_count,
            has_exam_request=has_exam_request,
        )
        book = _book(transaction)
        _seed_filing_rates(transaction, book)
        _seed_reexam_rates(transaction, book)

        candidates = SqlAlchemyOfficialFeeEstimateRateProvider(transaction).select_rate_candidates(
            command=command,
            rate_effective_on=EFFECTIVE_ON,
        )

        assert tuple(candidate.fee_code for candidate in candidates) == expected


@pytest.mark.parametrize(
    "trigger",
    (
        "LAYOUT_DESIGN_REGISTRATION",
        "PATENT_TERM_COMPENSATION",
        "OPEN_LICENSE_ANNUITY",
        "FILING_ACCEPTED ",
    ),
)
def test_unsupported_trigger_fails_before_any_sql(
    session_factory: sessionmaker,
    trigger: str,
) -> None:
    with session_factory() as transaction:
        command = PreviewFeeEstimateCommand(
            case_id="CASE-NOT-QUERIED",
            trigger_context=FeeEstimateContext(trigger=trigger, source_document_id=None),
            currency="CNY",
        )
        transaction.execute(text("SELECT 1"))
        before = _read_only_state(transaction)
        statements: list[str] = []

        def spy(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
            statements.append(statement)

        event.listen(transaction.bind, "before_cursor_execute", spy)
        try:
            with pytest.raises(FeeEstimatePreviewError) as caught:
                SqlAlchemyOfficialFeeEstimateRateProvider(transaction).select_rate_candidates(
                    command=command,
                    rate_effective_on=EFFECTIVE_ON,
                )
        finally:
            event.remove(transaction.bind, "before_cursor_execute", spy)
        assert caught.value.code is FeeEstimatePreviewErrorCode.TRIGGER_UNSUPPORTED
        assert caught.value.details == {"trigger": trigger}
        assert statements == []
        assert _read_only_state(transaction) == before


def test_direct_currency_date_and_case_facts_fail_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        case, command = _case(transaction)
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        _error(
            provider,
            PreviewFeeEstimateCommand(
                case_id=case.id,
                trigger_context=command.trigger_context,
                currency="USD",
            ),
            FeeEstimatePreviewErrorCode.INVALID_COMMAND,
            {"field": "currency"},
        )
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.INVALID_COMMAND,
            {"field": "rate_effective_on"},
            effective_on=datetime(2026, 7, 14),
        )
        missing = PreviewFeeEstimateCommand(
            case_id=str(uuid4()),
            trigger_context=command.trigger_context,
            currency="CNY",
        )
        _error(
            provider,
            missing,
            FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
            {"fee_code": None, "fee_year_key": 0, "field": "case_id"},
        )


@pytest.mark.parametrize(
    ("case_type", "flow_dir", "category", "claim_count", "has_exam_request", "field"),
    (
        ("PCT_INTL", "CN_DOMESTIC", "INV", 10, True, "case_type"),
        ("NORMAL", "PCT_NATL", "INV", 10, True, "flow_dir"),
        ("NORMAL", "CN_DOMESTIC", "OTHER", 10, True, "patent_category"),
        ("NORMAL", "CN_DOMESTIC", "INV", None, True, "claim_count"),
        ("NORMAL", "CN_DOMESTIC", "INV", 10, None, "has_exam_request"),
    ),
)
def test_unsupported_or_malformed_case_fact_fails_without_rate_inference(
    session_factory: sessionmaker,
    case_type: str,
    flow_dir: str,
    category: str,
    claim_count: int | None,
    has_exam_request: bool | None,
    field: str,
) -> None:
    with session_factory() as transaction:
        _, command = _case(
            transaction,
            case_type=case_type,
            flow_dir=flow_dir,
            category=category,
            claim_count=claim_count,
            has_exam_request=has_exam_request,
        )
        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
            {"fee_code": None, "fee_year_key": 0, "field": field},
        )


def test_book_and_rate_selection_fail_closed_with_exact_errors(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        code = "CN_UM_APPLICATION_FEE"
        missing_details = {
            "fee_code": code,
            "fee_year_key": 0,
            "rate_effective_on": EFFECTIVE_ON.isoformat(),
        }
        _error(provider, command, FeeEstimatePreviewErrorCode.RATE_MISSING, missing_details)

        book = _book(transaction)
        _error(provider, command, FeeEstimatePreviewErrorCode.RATE_MISSING, missing_details)
        rate = _rate(transaction, book, code)
        assert (
            provider.select_rate_candidates(command=command, rate_effective_on=EFFECTIVE_ON)[
                0
            ].source.rate_id
            == rate.id
        )

        transaction.execute(
            text("UPDATE t_fee_rate SET calc_mode = 'PER_CLAIM' WHERE id = :id"),
            {"id": rate.id},
        )
        transaction.commit()
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": code, "fee_year_key": 0, "field": "calc_mode"},
        )

        transaction.execute(
            text("UPDATE t_fee_rate SET calc_mode = 'FIXED' WHERE id = :id"),
            {"id": rate.id},
        )
        transaction.commit()
        _rate(transaction, book, code)
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
            missing_details,
        )


def test_book_interval_is_inclusive_and_provenance_corruption_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="DES", claim_count=10)
        book = _book(transaction, effective_from=EFFECTIVE_ON, effective_to=EFFECTIVE_ON)
        _rate(
            transaction,
            book,
            "CN_DES_APPLICATION_FEE",
            effective_from=EFFECTIVE_ON,
            effective_to=EFFECTIVE_ON,
        )
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        assert (
            len(provider.select_rate_candidates(command=command, rate_effective_on=EFFECTIVE_ON))
            == 1
        )

        transaction.execute(
            text("UPDATE t_fee_rate_book SET source_snapshot_hash = :hash WHERE id = :id"),
            {"hash": "c" * 64, "id": book.id},
        )
        transaction.commit()
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {
                "fee_code": "CN_DES_APPLICATION_FEE",
                "fee_year_key": 0,
                "field": "source_snapshot_hash",
            },
        )


def test_unapproved_or_multiple_effective_books_fail_closed(session_factory: sessionmaker) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        pending = _book(
            transaction,
            book_code="CNIPA-PENDING-FEES",
            approval_status="PENDING",
            activation_status="INACTIVE",
        )
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            {"fee_code": "CN_UM_APPLICATION_FEE", "fee_year_key": 0, "rate_id": None},
        )

        active = _book(transaction, book_code="CNIPA-ACTIVE-FEES")
        _rate(transaction, pending, "CN_UM_APPLICATION_FEE")
        _rate(transaction, active, "CN_UM_APPLICATION_FEE")
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
            {
                "fee_code": "CN_UM_APPLICATION_FEE",
                "fee_year_key": 0,
                "rate_effective_on": EFFECTIVE_ON.isoformat(),
            },
        )


@pytest.mark.parametrize(
    ("assignment", "value", "field"),
    (
        ("fee_name = :value", " ", "fee_name"),
        ("allow_reduction = :value", None, "allow_reduction"),
        ("default_amount = :value", 0, "default_amount"),
    ),
)
def test_malformed_linked_rate_fails_closed(
    session_factory: sessionmaker,
    assignment: str,
    value: object,
    field: str,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        transaction.execute(
            text(f"UPDATE t_fee_rate SET {assignment} WHERE id = :id"),
            {"value": value, "id": rate.id},
        )
        transaction.commit()

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": rate.fee_code, "fee_year_key": 0, "field": field},
        )


@pytest.mark.parametrize(
    ("assignment", "value"),
    (("currency = :value", "USD"), ("enabled = :value", 0)),
)
def test_disabled_or_wrong_currency_rate_is_missing_without_fallback(
    session_factory: sessionmaker,
    assignment: str,
    value: object,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        transaction.execute(
            text(f"UPDATE t_fee_rate SET {assignment} WHERE id = :id"),
            {"value": value, "id": rate.id},
        )
        transaction.commit()

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            {
                "fee_code": rate.fee_code,
                "fee_year_key": 0,
                "rate_effective_on": EFFECTIVE_ON.isoformat(),
            },
        )


def test_nonreducible_rate_forces_zero_and_skips_approval_select(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction="0.85",
        )
        book = _book(transaction)
        _rate(
            transaction,
            book,
            "CN_UM_APPLICATION_FEE",
            allow_reduction=False,
        )
        statements: list[str] = []

        def spy(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
            statements.append(statement)

        event.listen(transaction.bind, "before_cursor_execute", spy)
        try:
            (candidate,) = SqlAlchemyOfficialFeeEstimateRateProvider(
                transaction
            ).select_rate_candidates(command=command, rate_effective_on=EFFECTIVE_ON)
        finally:
            event.remove(transaction.bind, "before_cursor_execute", spy)

        assert candidate.reduction_input.reduction_ratio == Decimal("0")
        assert candidate.reduction_approval is None
        assert (
            len(
                [
                    statement
                    for statement in statements
                    if statement.lstrip().upper().startswith("SELECT")
                ]
            )
            == 2
        )


def test_exact_nonzero_reduction_maps_unique_confirmed_case_approval(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction="0.85",
        )
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        approval = _approval(
            transaction,
            case,
            ratio="0.85",
            fee_codes=(rate.fee_code,),
        )
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)

        (candidate,) = provider.select_rate_candidates(
            command=command,
            rate_effective_on=EFFECTIVE_ON,
        )

        assert candidate.reduction_input.reduction_ratio == Decimal("0.85")
        assert candidate.reduction_approval == FeeReductionApprovalContext(
            approval_id=approval.id,
            scope_type=FeeReductionApprovalScopeType.CASE,
            case_id=case.id,
            applicant_set_key=None,
            reduction_ratio=Decimal("0.8500"),
            fee_codes=frozenset({rate.fee_code}),
            fee_year_from=None,
            fee_year_to=None,
            effective_from=EFFECTIVE_ON,
            effective_to=EFFECTIVE_ON,
            source_evidence_version_id=approval.source_evidence_version_id,
            confirmation_status="CONFIRMED",
            is_current=True,
        )
        estimate = preview_estimate(
            command=command,
            rate_effective_on=EFFECTIVE_ON,
            rate_provider=provider,
        )
        assert estimate.total_payable_amount == Decimal("15.00")


@pytest.mark.parametrize("stored_ratio", (None, "0.70", "70%", " 0.7"))
def test_invalid_stored_reduction_ratio_fails_closed(
    session_factory: sessionmaker,
    stored_ratio: str | None,
) -> None:
    with session_factory() as transaction:
        _, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction=stored_ratio,
        )
        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
            {"fee_code": None, "fee_year_key": 0, "field": "fee_reduction"},
        )


def test_missing_duplicate_or_corrupt_reduction_approval_fails_closed(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction="0.7",
        )
        book = _book(transaction)
        _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        details = {
            "fee_code": "CN_UM_APPLICATION_FEE",
            "fee_year_key": 0,
            "field": "reduction_approval",
        }
        _error(provider, command, FeeEstimatePreviewErrorCode.CANDIDATE_INVALID, details)

        first = _approval(
            transaction,
            case,
            ratio="0.7",
            fee_codes=("CN_UM_APPLICATION_FEE",),
        )
        assert (
            len(provider.select_rate_candidates(command=command, rate_effective_on=EFFECTIVE_ON))
            == 1
        )
        _approval(
            transaction,
            case,
            ratio="0.7",
            fee_codes=("CN_UM_APPLICATION_FEE",),
        )
        _error(provider, command, FeeEstimatePreviewErrorCode.CANDIDATE_INVALID, details)

        transaction.execute(
            text("DELETE FROM t_fee_reduction_approval WHERE id != :id"),
            {"id": first.id},
        )
        transaction.execute(
            text("UPDATE t_fee_reduction_approval SET fee_scope_hash = :hash WHERE id = :id"),
            {"hash": "d" * 64, "id": first.id},
        )
        transaction.commit()
        _error(provider, command, FeeEstimatePreviewErrorCode.CANDIDATE_INVALID, details)


@pytest.mark.parametrize(
    ("assignment", "values", "ignore_checks", "field"),
    (
        (
            "source_reference = :value",
            {"value": "https://example.test/not-cnipa"},
            False,
            "source_reference",
        ),
        (
            "current_identity_key = NULL",
            {},
            True,
            "current_identity_key",
        ),
        (
            "source_version = :value",
            {"value": " "},
            False,
            "source_version",
        ),
        (
            "source_published_on = :value",
            {"value": "2026-07-13"},
            False,
            "source_published_on",
        ),
    ),
)
def test_rate_book_trust_current_identity_and_provenance_corruption_fail_closed(
    session_factory: sessionmaker,
    assignment: str,
    values: dict[str, object],
    ignore_checks: bool,
    field: str,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        _unsafe_update(
            transaction,
            "t_fee_rate_book",
            assignment,
            row_id=book.id,
            values=values,
            ignore_checks=ignore_checks,
        )

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": "CN_UM_APPLICATION_FEE", "fee_year_key": 0, "field": field},
        )


def test_retired_rate_book_is_unapproved_and_never_selected(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        _unsafe_update(
            transaction,
            "t_fee_rate_book",
            "activation_status = 'RETIRED', current_identity_key = NULL",
            row_id=book.id,
            values={},
        )

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            {"fee_code": rate.fee_code, "fee_year_key": 0, "rate_id": None},
        )


@pytest.mark.parametrize(
    ("mutation", "ignore_checks"),
    (("official_rate_book_id = NULL", False), ("fee_type = 'SERVICE'", True)),
)
def test_unlinked_or_non_gov_rate_is_missing_without_fallback(
    session_factory: sessionmaker,
    mutation: str,
    ignore_checks: bool,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        _unsafe_update(
            transaction,
            "t_fee_rate",
            mutation,
            row_id=rate.id,
            values={},
            ignore_checks=ignore_checks,
        )

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            {
                "fee_code": rate.fee_code,
                "fee_year_key": 0,
                "rate_effective_on": EFFECTIVE_ON.isoformat(),
            },
        )


def test_rate_interval_is_inclusive_but_out_of_range_is_missing(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(
            transaction,
            book,
            "CN_UM_APPLICATION_FEE",
            effective_from=EFFECTIVE_ON,
            effective_to=EFFECTIVE_ON,
        )
        provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
        assert (
            provider.select_rate_candidates(
                command=command,
                rate_effective_on=EFFECTIVE_ON,
            )[0].source.rate_id
            == rate.id
        )

        _unsafe_update(
            transaction,
            "t_fee_rate",
            "effective_from = :effective_from, effective_to = NULL",
            row_id=rate.id,
            values={"effective_from": "2026-07-15"},
        )
        _error(
            provider,
            command,
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            {
                "fee_code": rate.fee_code,
                "fee_year_key": 0,
                "rate_effective_on": EFFECTIVE_ON.isoformat(),
            },
        )


def test_rate_amount_with_more_than_two_stored_decimal_places_is_invalid(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        _unsafe_update(
            transaction,
            "t_fee_rate",
            "default_amount = :value",
            row_id=rate.id,
            values={"value": 100.001},
        )

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": rate.fee_code, "fee_year_key": 0, "field": "default_amount"},
        )


@pytest.mark.parametrize(
    ("case_ratio", "approval_changes"),
    (
        ("0.7", {"ratio": "0.85"}),
        ("0.7", {"scope_type": "APPLICANT_SET"}),
        ("0.7", {"fee_codes": ("CN_OTHER_FEE",)}),
        ("0.7", {"fee_year_from": 1, "fee_year_to": 1}),
        (
            "0.7",
            {"effective_from": date(2026, 7, 15), "effective_to": date(2026, 7, 15)},
        ),
        ("0.7", {"status": "REJECTED"}),
    ),
)
def test_wrong_approval_ratio_scope_fee_year_date_status_and_applicant_set_fail_closed(
    session_factory: sessionmaker,
    case_ratio: str,
    approval_changes: dict[str, object],
) -> None:
    with session_factory() as transaction:
        case, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction=case_ratio,
        )
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        values: dict[str, object] = {
            "ratio": case_ratio,
            "fee_codes": (rate.fee_code,),
        }
        values.update(approval_changes)
        _approval(transaction, case, **values)  # type: ignore[arg-type]

        _error(
            SqlAlchemyOfficialFeeEstimateRateProvider(transaction),
            command,
            FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
            {"fee_code": rate.fee_code, "fee_year_key": 0, "field": "reduction_approval"},
        )


def test_sql_order_count_tie_breaks_and_success_state_are_deterministic(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case, command = _case(
            transaction,
            category="UM",
            claim_count=10,
            fee_reduction="0.85",
        )
        book = _book(transaction)
        rate = _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        _approval(transaction, case, ratio="0.85", fee_codes=(rate.fee_code,))
        transaction.execute(text("SELECT 1"))
        before = _read_only_state(transaction)
        statements: list[str] = []

        def spy(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(" ".join(statement.split()))

        event.listen(transaction.bind, "before_cursor_execute", spy)
        try:
            provider = SqlAlchemyOfficialFeeEstimateRateProvider(transaction)
            first = provider.select_rate_candidates(
                command=command,
                rate_effective_on=EFFECTIVE_ON,
            )
            first_statements = tuple(statements)
            statements.clear()
            second = provider.select_rate_candidates(
                command=command,
                rate_effective_on=EFFECTIVE_ON,
            )
            second_statements = tuple(statements)
        finally:
            event.remove(transaction.bind, "before_cursor_execute", spy)

        assert first == second
        assert first_statements == second_statements
        assert len(first_statements) == 3
        assert "ORDER BY t_case.id" in first_statements[0]
        assert (
            "ORDER BY t_fee_rate_book.id, t_fee_rate.fee_code, t_fee_rate.id" in first_statements[1]
        )
        assert "ORDER BY t_fee_reduction_approval.id" in first_statements[2]
        assert _read_only_state(transaction) == before


def test_forbidden_write_transaction_clock_uuid_network_and_fallback_calls_fail_immediately(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with session_factory() as transaction:
        _, command = _case(transaction, category="UM", claim_count=10)
        book = _book(transaction)
        _rate(transaction, book, "CN_UM_APPLICATION_FEE")
        transaction.execute(text("SELECT 1"))

        def forbidden(*_args, **_kwargs):
            pytest.fail("read-only provider invoked a forbidden dependency")

        before = _read_only_state(transaction)
        with monkeypatch.context() as guarded:
            uuid4_code = uuid.uuid4.__code__
            for method in (
                "add",
                "add_all",
                "delete",
                "flush",
                "commit",
                "rollback",
                "begin",
                "begin_nested",
                "close",
            ):
                guarded.setattr(transaction, method, forbidden)
            guarded.setattr(socket, "create_connection", forbidden)
            guarded.setattr(urllib.request, "urlopen", forbidden)
            guarded.setattr(uuid, "uuid4", forbidden)
            guarded.setattr(fee_models_module, "uuid4", forbidden)
            guarded.setattr(obligation_service_module, "uuid4", forbidden)
            guarded.setattr(obligation_service_module, "validate_fee_reduction", forbidden)
            guarded.setattr(obligation_service_module, "recognize_obligation", forbidden)
            guarded.setattr(seed_dev, "seed_official_fee_rate_catalog", forbidden)
            guarded.setattr(official_rate_book_module, "activate_official_rate_book", forbidden)
            guarded.setattr(official_rate_book_module, "_current_row", forbidden)
            guarded.setattr(official_rate_book_module, "_validate_source", forbidden)

            forbidden_c_calls = {datetime.now, date.today}

            def profile(frame, profile_event, arg):
                if profile_event == "c_call" and arg in forbidden_c_calls:
                    pytest.fail("read-only provider read the clock")
                if profile_event == "call" and frame.f_code is uuid4_code:
                    pytest.fail("read-only provider generated a UUID")

            sys.setprofile(profile)
            try:
                candidates = SqlAlchemyOfficialFeeEstimateRateProvider(
                    transaction
                ).select_rate_candidates(command=command, rate_effective_on=EFFECTIVE_ON)
            finally:
                sys.setprofile(None)

        assert len(candidates) == 1
        assert type(candidates[0]) is OfficialFeeEstimateRateCandidate
        assert _read_only_state(transaction) == before
