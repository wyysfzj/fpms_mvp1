from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

from sqlalchemy import String, and_, cast, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Bundle, Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.fees.fee_reduction import (
    FeeReductionApprovalContext,
    FeeReductionApprovalScopeType,
    FeeReductionEvaluationContext,
    FeeReductionInput,
    FeeReductionInputProvenance,
)
from app.modules.fees.models import FeeRate, FeeReductionApproval, OfficialRateBook
from app.modules.fees.obligation_contracts import (
    FeeEstimateSource,
    FeeSourceStatus,
    PreviewFeeEstimateCommand,
)
from app.modules.fees.obligation_service import (
    FeeEstimatePreviewError,
    FeeEstimatePreviewErrorCode,
    OfficialFeeEstimateRateCandidate,
)

__all__ = (
    "ActivateOfficialRateBookCommand",
    "ActivateOfficialRateBookResult",
    "CalculateCompensationPeriodAnnuityFeeCommand",
    "CalculateCompensationPeriodAnnuityFeeResult",
    "CalculateOpenLicenseAnnuityReductionCommand",
    "CalculateOpenLicenseAnnuityReductionResult",
    "GetLayoutRegistrationFeeCommand",
    "GetLayoutRegistrationFeeResult",
    "GetLayoutBibliographicChangeFeeCommand",
    "GetLayoutBibliographicChangeFeeResult",
    "GetLayoutExtensionFeeCommand",
    "GetLayoutExtensionFeeResult",
    "GetLayoutNonvoluntaryLicenseFeeCommand",
    "GetLayoutNonvoluntaryLicenseFeeResult",
    "GetLayoutRemunerationAdjudicationFeeCommand",
    "GetLayoutRemunerationAdjudicationFeeResult",
    "GetPatentTermCompensationRequestFeeCommand",
    "GetPatentTermCompensationRequestFeeResult",
    "GetLayoutReexaminationFeeCommand",
    "GetLayoutReexaminationFeeResult",
    "GetLayoutRestorationFeeCommand",
    "GetLayoutRestorationFeeResult",
    "OfficialRateBookActivationDisposition",
    "SqlAlchemyOfficialFeeEstimateRateProvider",
    "activate_official_rate_book",
    "calculate_compensation_period_annuity_fee",
    "calculate_open_license_annuity_reduction",
    "get_layout_registration_fee",
    "get_layout_bibliographic_change_fee",
    "get_layout_extension_fee",
    "get_layout_nonvoluntary_license_fee",
    "get_layout_remuneration_adjudication_fee",
    "get_patent_term_compensation_request_fee",
    "get_layout_reexamination_fee",
    "get_layout_restoration_fee",
)


class OfficialRateBookActivationDisposition(str, Enum):
    ACTIVATED = "ACTIVATED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class ActivateOfficialRateBookCommand:
    rate_book_id: str
    approved_by: str
    approved_at: datetime
    activated_by: str
    activated_at: datetime
    expected_current_rate_book_id: str | None


@dataclass(frozen=True)
class ActivateOfficialRateBookResult:
    rate_book_id: str
    book_code: str
    version_code: str
    effective_from: date
    effective_to: date | None
    approval_status: str
    activation_status: str
    disposition: OfficialRateBookActivationDisposition


@dataclass(frozen=True, slots=True)
class CalculateCompensationPeriodAnnuityFeeCommand:
    effective_date: date
    complete_years: int


@dataclass(frozen=True, slots=True)
class CalculateCompensationPeriodAnnuityFeeResult:
    fee_code: str
    currency: str
    complete_years: int
    unit_amount: Decimal
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class CalculateOpenLicenseAnnuityReductionCommand:
    existing_reduction_ratio: Decimal


@dataclass(frozen=True, slots=True)
class CalculateOpenLicenseAnnuityReductionResult:
    open_license_reduction_ratio: Decimal
    existing_reduction_ratio: Decimal
    applied_reduction_ratio: Decimal
    payable_ratio: Decimal


@dataclass(frozen=True, slots=True)
class GetLayoutRegistrationFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutRegistrationFeeResult:
    rate_id: str
    fee_code: str
    fee_type: str
    currency: str
    calc_mode: str
    allow_reduction: bool
    enabled: bool
    amount: Decimal
    rate_book_id: str
    book_code: str
    version_code: str
    effective_from: date
    effective_to: date | None
    approval_status: str
    activation_status: str
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutBibliographicChangeFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutBibliographicChangeFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutExtensionFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutExtensionFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutNonvoluntaryLicenseFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutNonvoluntaryLicenseFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutRemunerationAdjudicationFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutRemunerationAdjudicationFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetPatentTermCompensationRequestFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetPatentTermCompensationRequestFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutReexaminationFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutReexaminationFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


@dataclass(frozen=True, slots=True)
class GetLayoutRestorationFeeCommand:
    effective_date: date


@dataclass(frozen=True, slots=True)
class GetLayoutRestorationFeeResult:
    fee_code: str
    currency: str
    amount: Decimal
    effective_from: date
    source_reference: str
    source_version: str
    source_snapshot_hash: str


_SOURCE_SCHEMA = "CNIPA_RATE_SOURCE_V1"
_SOURCE_KEYS = {
    "content_sha256",
    "document_no",
    "published_on",
    "retrieved_at",
    "title",
    "url",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")


def _fail(
    code: str,
    message: str,
    *,
    status_code: int,
    details: dict[str, str | None],
) -> None:
    raise_business_error(
        code,
        message,
        details=details,
        status_code=status_code,
    )


def _invalid_input(field: str) -> None:
    _fail(
        "OFFICIAL_RATE_BOOK_INVALID_INPUT",
        "Invalid official rate book activation input",
        status_code=400,
        details={"field": field},
    )


def _source_invalid(rate_book_id: str, field: str) -> None:
    _fail(
        "OFFICIAL_RATE_BOOK_SOURCE_INVALID",
        "Official rate book source is invalid",
        status_code=409,
        details={"rate_book_id": rate_book_id, "field": field},
    )


def _source_untrusted(rate_book_id: str, field: str) -> None:
    _fail(
        "OFFICIAL_RATE_BOOK_SOURCE_UNTRUSTED",
        "Official rate book source is not trusted",
        status_code=409,
        details={"rate_book_id": rate_book_id, "field": field},
    )


def _state_conflict(rate_book_id: str, field: str) -> None:
    _fail(
        "OFFICIAL_RATE_BOOK_STATE_CONFLICT",
        "Official rate book state conflicts with activation",
        status_code=409,
        details={"rate_book_id": rate_book_id, "field": field},
    )


def _canonical_uuid(value: object, field: str) -> str:
    if type(value) is not str:
        _invalid_input(field)
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _invalid_input(field)
    if str(parsed) != value:
        _invalid_input(field)
    return value


def _naive_datetime(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.utcoffset() is not None:
        _invalid_input(field)
    return value


def _validate_command(command: object, transaction: object) -> ActivateOfficialRateBookCommand:
    if type(command) is not ActivateOfficialRateBookCommand:
        _invalid_input("command")
    if not isinstance(transaction, Session):
        _invalid_input("transaction")

    _canonical_uuid(command.rate_book_id, "rate_book_id")
    _canonical_uuid(command.approved_by, "approved_by")
    _canonical_uuid(command.activated_by, "activated_by")
    if command.expected_current_rate_book_id is not None:
        _canonical_uuid(
            command.expected_current_rate_book_id,
            "expected_current_rate_book_id",
        )
    approved_at = _naive_datetime(command.approved_at, "approved_at")
    activated_at = _naive_datetime(command.activated_at, "activated_at")
    if approved_at > activated_at:
        _invalid_input("approved_at/activated_at")
    return command


def _exact_string(value: object, *, limit: int | None = None) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value == value.strip()
        and (limit is None or len(value) <= limit)
    )


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _SHA256_RE.fullmatch(value) is not None


def _valid_date_text(value: object) -> bool:
    if type(value) is not str or _DATE_RE.fullmatch(value) is None:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _valid_utc_timestamp(value: object) -> bool:
    if type(value) is not str or _UTC_TIMESTAMP_RE.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError:
        return False
    return parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0


def _trusted_cnipa_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return (
        value.startswith("https://")
        and parsed.scheme == "https"
        and parsed.hostname == "www.cnipa.gov.cn"
        and parsed.netloc == "www.cnipa.gov.cn"
        and not parsed.query
        and not parsed.fragment
        and urlunsplit(parsed) == value
    )


def _validate_source(row: OfficialRateBook) -> None:
    if row.source_authority != "CNIPA":
        _source_untrusted(row.id, "source_authority")

    exact_fields = (
        ("book_code", row.book_code, 64),
        ("version_code", row.version_code, 128),
        ("source_reference", row.source_reference, 512),
        ("source_version", row.source_version, 128),
    )
    for field, value, limit in exact_fields:
        if not _exact_string(value, limit=limit):
            _source_invalid(row.id, field)
    if not _trusted_cnipa_url(row.source_reference):
        _source_untrusted(row.id, "source_reference")

    if type(row.effective_from) is not date:
        _source_invalid(row.id, "effective_from")
    if row.effective_to is not None and type(row.effective_to) is not date:
        _source_invalid(row.id, "effective_to")
    if row.effective_to is not None and row.effective_to < row.effective_from:
        _source_invalid(row.id, "effective_to")
    if type(row.source_published_on) is not date:
        _source_invalid(row.id, "source_published_on")
    if not _valid_sha256(row.source_snapshot_hash):
        _source_invalid(row.id, "source_snapshot_hash")
    if type(row.source_snapshot) is not str:
        _source_invalid(row.id, "source_snapshot")

    try:
        snapshot = json.loads(row.source_snapshot)
        canonical = json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _source_invalid(row.id, "source_snapshot")
    if canonical != row.source_snapshot:
        _source_invalid(row.id, "source_snapshot")
    try:
        snapshot_bytes = row.source_snapshot.encode("utf-8")
    except UnicodeEncodeError:
        _source_invalid(row.id, "source_snapshot")
    if hashlib.sha256(snapshot_bytes).hexdigest() != row.source_snapshot_hash:
        _source_invalid(row.id, "source_snapshot_hash")
    if type(snapshot) is not dict or set(snapshot) != {"schema_version", "sources"}:
        _source_invalid(row.id, "source_snapshot")
    if snapshot["schema_version"] != _SOURCE_SCHEMA:
        _source_invalid(row.id, "schema_version")
    sources = snapshot["sources"]
    if type(sources) is not list or not sources:
        _source_invalid(row.id, "sources")

    for source in sources:
        if type(source) is not dict or set(source) != _SOURCE_KEYS:
            _source_invalid(row.id, "sources")
        if not _valid_sha256(source["content_sha256"]):
            _source_invalid(row.id, "content_sha256")
        document_no = source["document_no"]
        if document_no is not None and not _exact_string(document_no):
            _source_invalid(row.id, "document_no")
        if not _valid_date_text(source["published_on"]):
            _source_invalid(row.id, "published_on")
        if not _valid_utc_timestamp(source["retrieved_at"]):
            _source_invalid(row.id, "retrieved_at")
        if not _exact_string(source["title"]):
            _source_invalid(row.id, "title")
        if not _exact_string(source["url"]):
            _source_invalid(row.id, "url")
        if not _trusted_cnipa_url(source["url"]):
            _source_untrusted(row.id, "url")

    first = sources[0]
    if first["url"] != row.source_reference:
        _source_invalid(row.id, "source_reference")
    if first["published_on"] != row.source_published_on.isoformat():
        _source_invalid(row.id, "source_published_on")


def _validate_actors(command: ActivateOfficialRateBookCommand, transaction: Session) -> None:
    actor_ids = {command.approved_by, command.activated_by}
    actors = {
        actor.id: actor
        for actor in transaction.scalars(select(T_User).where(T_User.id.in_(actor_ids))).all()
    }
    for field, actor_id in (
        ("approved_by", command.approved_by),
        ("activated_by", command.activated_by),
    ):
        actor = actors.get(actor_id)
        if actor is None:
            _fail(
                "OFFICIAL_RATE_BOOK_ACTOR_NOT_FOUND",
                "Official rate book actor not found",
                status_code=404,
                details={"field": field, "actor_id": actor_id},
            )
        if actor.is_active is not True:
            _fail(
                "OFFICIAL_RATE_BOOK_ACTOR_INACTIVE",
                "Official rate book actor is inactive",
                status_code=409,
                details={"field": field, "actor_id": actor_id},
            )


def _active_tuple_matches(
    row: OfficialRateBook,
    command: ActivateOfficialRateBookCommand,
) -> bool:
    return (
        row.approval_status == "APPROVED"
        and row.approved_by == command.approved_by
        and row.approved_at == command.approved_at
        and row.activation_status == "ACTIVE"
        and row.activated_by == command.activated_by
        and row.activated_at == command.activated_at
        and row.current_identity_key == f"CNIPA|{row.book_code}"
    )


def _validate_state_or_replay(
    row: OfficialRateBook,
    command: ActivateOfficialRateBookCommand,
) -> ActivateOfficialRateBookResult | None:
    if row.activation_status == "ACTIVE":
        stored_tuple_is_consistent = (
            row.approval_status == "APPROVED"
            and row.approved_by is not None
            and row.approved_at is not None
            and row.activated_by is not None
            and row.activated_at is not None
            and row.current_identity_key == f"CNIPA|{row.book_code}"
        )
        if not stored_tuple_is_consistent:
            _state_conflict(row.id, "approval_status/activation_status")
        if _active_tuple_matches(row, command):
            return _result(row, OfficialRateBookActivationDisposition.REUSED)
        _fail(
            "OFFICIAL_RATE_BOOK_ACTIVATION_PAYLOAD_CONFLICT",
            "Official rate book activation payload conflicts with first activation",
            status_code=409,
            details={"rate_book_id": row.id},
        )

    if row.activation_status != "INACTIVE":
        _state_conflict(row.id, "activation_status")
    if any(
        value is not None
        for value in (row.activated_by, row.activated_at, row.current_identity_key)
    ):
        _state_conflict(row.id, "activation_status")

    if row.approval_status == "PENDING":
        if row.approved_by is not None or row.approved_at is not None:
            _state_conflict(row.id, "approval_status")
        return None
    if row.approval_status == "APPROVED":
        if row.approved_by != command.approved_by or row.approved_at != command.approved_at:
            _state_conflict(row.id, "approval_status")
        return None
    _state_conflict(row.id, "approval_status")


def _current_row(
    transaction: Session,
    current_identity_key: str,
) -> OfficialRateBook | None:
    return transaction.scalar(
        select(OfficialRateBook).where(
            OfficialRateBook.current_identity_key == current_identity_key
        )
    )


def _raise_current_conflict(
    row: OfficialRateBook,
    command: ActivateOfficialRateBookCommand,
    actual_current_id: str | None,
) -> None:
    _fail(
        "OFFICIAL_RATE_BOOK_CURRENT_IDENTITY_CONFLICT",
        "Official rate book current identity conflict",
        status_code=409,
        details={
            "rate_book_id": row.id,
            "expected_current_rate_book_id": command.expected_current_rate_book_id,
            "actual_current_rate_book_id": actual_current_id,
        },
    )


def _validate_intervals(row: OfficialRateBook, transaction: Session) -> None:
    other_rows = transaction.scalars(
        select(OfficialRateBook).where(
            OfficialRateBook.id != row.id,
            OfficialRateBook.source_authority == row.source_authority,
            OfficialRateBook.book_code == row.book_code,
            OfficialRateBook.activation_status.in_(("ACTIVE", "RETIRED")),
        )
    ).all()
    for other in other_rows:
        row_starts_before_other_ends = (
            other.effective_to is None or row.effective_from <= other.effective_to
        )
        other_starts_before_row_ends = (
            row.effective_to is None or other.effective_from <= row.effective_to
        )
        if row_starts_before_other_ends and other_starts_before_row_ends:
            _fail(
                "OFFICIAL_RATE_BOOK_INTERVAL_OVERLAP",
                "Official rate book effective interval overlaps history",
                status_code=409,
                details={"rate_book_id": row.id, "overlap_rate_book_id": other.id},
            )


def _result(
    row: OfficialRateBook,
    disposition: OfficialRateBookActivationDisposition,
) -> ActivateOfficialRateBookResult:
    return ActivateOfficialRateBookResult(
        rate_book_id=row.id,
        book_code=row.book_code,
        version_code=row.version_code,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        approval_status=row.approval_status,
        activation_status=row.activation_status,
        disposition=disposition,
    )


def activate_official_rate_book(
    command: ActivateOfficialRateBookCommand,
    transaction: Session,
) -> ActivateOfficialRateBookResult:
    command = _validate_command(command, transaction)
    row = transaction.get(OfficialRateBook, command.rate_book_id)
    if row is None:
        _fail(
            "OFFICIAL_RATE_BOOK_NOT_FOUND",
            "Official rate book candidate not found",
            status_code=404,
            details={"rate_book_id": command.rate_book_id},
        )

    _validate_source(row)
    _validate_actors(command, transaction)
    replay = _validate_state_or_replay(row, command)
    if replay is not None:
        return replay

    current_identity_key = f"CNIPA|{row.book_code}"
    current = _current_row(transaction, current_identity_key)
    actual_current_id = current.id if current is not None else None
    if actual_current_id != command.expected_current_rate_book_id:
        _raise_current_conflict(row, command, actual_current_id)
    _validate_intervals(row, transaction)

    nested_transaction = transaction.begin_nested()
    try:
        with nested_transaction:
            if current is not None:
                current.activation_status = "RETIRED"
                current.current_identity_key = None
                current.updated_by = command.activated_by
                current.updated_at = command.activated_at
                transaction.flush()

            if row.approval_status == "PENDING":
                row.approval_status = "APPROVED"
                row.approved_by = command.approved_by
                row.approved_at = command.approved_at
            row.activation_status = "ACTIVE"
            row.activated_by = command.activated_by
            row.activated_at = command.activated_at
            row.current_identity_key = current_identity_key
            row.updated_by = command.activated_by
            row.updated_at = command.activated_at
            transaction.flush()
    except IntegrityError:
        transaction.expire_all()
        winner = transaction.get(
            OfficialRateBook,
            command.rate_book_id,
            populate_existing=True,
        )
        if winner is not None and _active_tuple_matches(winner, command):
            return _result(winner, OfficialRateBookActivationDisposition.REUSED)
        actual_current = _current_row(transaction, current_identity_key)
        _raise_current_conflict(
            row,
            command,
            actual_current.id if actual_current is not None else None,
        )

    return _result(row, OfficialRateBookActivationDisposition.ACTIVATED)


_PROVIDER_SUPPORTED_TRIGGERS = frozenset(("FILING_ACCEPTED", "REEXAM_REQUESTED"))
_PROVIDER_RATIO_BY_STORED_VALUE = {
    "0": Decimal("0"),
    "0.7": Decimal("0.7"),
    "0.85": Decimal("0.85"),
}
_PROVIDER_TWO_PLACES = Decimal("0.01")
_FEE_SCOPE_SCHEMA = "FPMS_FEE_REDUCTION_FEE_SCOPE_V1"
_ELIGIBILITY_SCHEMA = "FPMS_FEE_REDUCTION_ELIGIBILITY_V1"


@dataclass(frozen=True, slots=True)
class _RequiredRate:
    fee_code: str
    calc_mode: str
    quantity: int


@dataclass(frozen=True, slots=True)
class _CaseFacts:
    id: str
    fee_reduction: Decimal


@dataclass(frozen=True, slots=True)
class _ProviderBook:
    id: str
    book_code: str
    version_code: str
    source_authority: str
    source_reference: str
    source_version: str
    source_published_on: date
    source_snapshot: str
    source_snapshot_hash: str
    approval_status: str
    approved_by: str | None
    approved_at: datetime | None
    effective_from: date
    effective_to: date | None
    activation_status: str
    activated_by: str | None
    activated_at: datetime | None
    current_identity_key: str | None


@dataclass(frozen=True, slots=True)
class _ProviderRate:
    id: str
    fee_code: str
    fee_name: str | None
    fee_type: str
    currency: str
    default_amount: Decimal | None
    enabled: bool
    calc_mode: str | None
    allow_reduction: bool | None
    effective_from: date | None
    effective_to: date | None
    official_rate_book_id: str | None


@dataclass(frozen=True, slots=True)
class _ProviderApproval:
    id: str
    scope_type: str
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_scope_snapshot: str
    fee_scope_hash: str
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    confirmed_at: datetime | None
    confirmed_by: str | None
    eligibility_snapshot: str
    eligibility_snapshot_hash: str
    approval_identity_key: str


def _provider_raise(
    code: FeeEstimatePreviewErrorCode,
    details: dict[str, str | int | bool | None],
) -> None:
    raise FeeEstimatePreviewError(code, details)


def _provider_candidate_invalid(fee_code: str | None, field: str) -> None:
    _provider_raise(
        FeeEstimatePreviewErrorCode.CANDIDATE_INVALID,
        {"fee_code": fee_code, "fee_year_key": 0, "field": field},
    )


def _provider_rate_details(fee_code: str, rate_effective_on: date) -> dict[str, str | int]:
    return {
        "fee_code": fee_code,
        "fee_year_key": 0,
        "rate_effective_on": rate_effective_on.isoformat(),
    }


def _provider_case_facts(
    transaction: Session,
    command: PreviewFeeEstimateCommand,
    trigger: str,
) -> tuple[_CaseFacts, tuple[_RequiredRate, ...]]:
    row = transaction.execute(
        select(
            Case.id,
            Case.case_type,
            Case.flow_dir,
            Case.patent_category,
            Case.claim_count,
            Case.has_exam_request,
            Case.fee_reduction,
        )
        .where(Case.id == command.case_id)
        .order_by(Case.id)
    ).one_or_none()
    if row is None:
        _provider_candidate_invalid(None, "case_id")
    if type(row.case_type) is not str or row.case_type != "NORMAL":
        _provider_candidate_invalid(None, "case_type")
    if type(row.flow_dir) is not str or row.flow_dir != "CN_DOMESTIC":
        _provider_candidate_invalid(None, "flow_dir")
    if type(row.patent_category) is not str or row.patent_category not in {"INV", "UM", "DES"}:
        _provider_candidate_invalid(None, "patent_category")
    if (
        type(row.fee_reduction) is not str
        or row.fee_reduction not in _PROVIDER_RATIO_BY_STORED_VALUE
    ):
        _provider_candidate_invalid(None, "fee_reduction")
    facts = _CaseFacts(
        id=row.id,
        fee_reduction=_PROVIDER_RATIO_BY_STORED_VALUE[row.fee_reduction],
    )

    if trigger == "REEXAM_REQUESTED":
        return facts, (
            _RequiredRate(
                {
                    "INV": "CN_REEXAM_FEE_INV",
                    "UM": "CN_REEXAM_FEE_UM",
                    "DES": "CN_REEXAM_FEE_DES",
                }[row.patent_category],
                "FIXED",
                1,
            ),
        )

    if type(row.claim_count) is not int or type(row.claim_count) is bool or row.claim_count < 0:
        _provider_candidate_invalid(None, "claim_count")
    if row.patent_category == "INV" and type(row.has_exam_request) is not bool:
        _provider_candidate_invalid(None, "has_exam_request")

    required = [
        _RequiredRate(
            {
                "INV": "CN_INV_APPLICATION_FEE",
                "UM": "CN_UM_APPLICATION_FEE",
                "DES": "CN_DES_APPLICATION_FEE",
            }[row.patent_category],
            "FIXED",
            1,
        )
    ]
    if row.claim_count > 10:
        required.append(_RequiredRate("CN_EXCESS_CLAIM_FEE", "PER_CLAIM", row.claim_count - 10))
    if row.patent_category == "INV":
        required.append(_RequiredRate("CN_PUBLICATION_PRINT_FEE", "FIXED", 1))
        if row.has_exam_request is True:
            required.append(_RequiredRate("CN_SUBSTANTIVE_EXAM_FEE", "FIXED", 1))
    return facts, tuple(required)


def _provider_canonical_json(value: object) -> object | None:
    if type(value) is not str:
        return None
    try:
        parsed = json.loads(value)
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return None
    return parsed if canonical == value else None


def _provider_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _provider_book_invalid_field(book: _ProviderBook) -> str | None:
    if book.source_authority != "CNIPA":
        return "source_authority"
    for field in ("id", "book_code", "version_code", "source_version", "source_reference"):
        if not _exact_string(getattr(book, field)):
            return field
    if book.current_identity_key != f"CNIPA|{book.book_code}":
        return "current_identity_key"
    if not _trusted_cnipa_url(book.source_reference):
        return "source_reference"
    if type(book.effective_from) is not date:
        return "effective_from"
    if book.effective_to is not None and type(book.effective_to) is not date:
        return "effective_to"
    if book.effective_to is not None and book.effective_to < book.effective_from:
        return "effective_to"
    if not _exact_string(book.approved_by) or type(book.approved_at) is not datetime:
        return "approval_status"
    if not _exact_string(book.activated_by) or type(book.activated_at) is not datetime:
        return "activation_status"
    if type(book.source_published_on) is not date:
        return "source_published_on"
    if not _valid_sha256(book.source_snapshot_hash):
        return "source_snapshot_hash"
    parsed = _provider_canonical_json(book.source_snapshot)
    if type(parsed) is not dict:
        return "source_snapshot"
    try:
        snapshot_hash = hashlib.sha256(book.source_snapshot.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        return "source_snapshot"
    if snapshot_hash != book.source_snapshot_hash:
        return "source_snapshot_hash"
    if set(parsed) != {"schema_version", "sources"}:
        return "source_snapshot"
    if parsed["schema_version"] != _SOURCE_SCHEMA:
        return "schema_version"
    sources = parsed["sources"]
    if type(sources) is not list or not sources:
        return "sources"
    for source in sources:
        if type(source) is not dict or set(source) != _SOURCE_KEYS:
            return "sources"
        if not _valid_sha256(source["content_sha256"]):
            return "content_sha256"
        if source["document_no"] is not None and not _exact_string(source["document_no"]):
            return "document_no"
        if not _valid_date_text(source["published_on"]):
            return "published_on"
        if not _valid_utc_timestamp(source["retrieved_at"]):
            return "retrieved_at"
        if not _exact_string(source["title"]):
            return "title"
        if not _exact_string(source["url"]) or not _trusted_cnipa_url(source["url"]):
            return "url"
    first = sources[0]
    if first["url"] != book.source_reference:
        return "source_reference"
    if first["published_on"] != book.source_published_on.isoformat():
        return "source_published_on"
    return None


def _provider_rate_amount(
    row: _ProviderRate,
    required: _RequiredRate,
    raw_default_amount: str | None,
) -> Decimal:
    checks = (
        ("rate_id", _exact_string(row.id)),
        ("fee_code", row.fee_code == required.fee_code),
        ("fee_name", _exact_string(row.fee_name)),
        ("fee_type", row.fee_type == "GOV"),
        ("currency", row.currency == "CNY"),
        ("enabled", row.enabled is True),
        ("calc_mode", row.calc_mode == required.calc_mode),
        ("allow_reduction", type(row.allow_reduction) is bool),
    )
    for field, valid in checks:
        if not valid:
            _provider_raise(
                FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
                {"fee_code": required.fee_code, "fee_year_key": 0, "field": field},
            )
    amount = row.default_amount
    if type(amount) is not Decimal or not amount.is_finite() or amount <= 0:
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": required.fee_code, "fee_year_key": 0, "field": "default_amount"},
        )
    try:
        stored_amount = Decimal(raw_default_amount) if raw_default_amount is not None else None
        if (
            stored_amount is None
            or not stored_amount.is_finite()
            or stored_amount <= 0
            or stored_amount != amount
            or stored_amount != stored_amount.quantize(_PROVIDER_TWO_PLACES)
            or amount != amount.quantize(_PROVIDER_TWO_PLACES)
        ):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": required.fee_code, "fee_year_key": 0, "field": "default_amount"},
        )
    return amount * required.quantity


def _provider_rate_rows(
    transaction: Session,
    required_rates: tuple[_RequiredRate, ...],
    rate_effective_on: date,
) -> tuple[_ProviderBook, tuple[tuple[_RequiredRate, _ProviderRate, Decimal], ...]]:
    required_codes = tuple(required.fee_code for required in required_rates)
    book_bundle = Bundle(
        "book",
        OfficialRateBook.id,
        OfficialRateBook.book_code,
        OfficialRateBook.version_code,
        OfficialRateBook.source_authority,
        OfficialRateBook.source_reference,
        OfficialRateBook.source_version,
        OfficialRateBook.source_published_on,
        OfficialRateBook.source_snapshot,
        OfficialRateBook.source_snapshot_hash,
        OfficialRateBook.approval_status,
        OfficialRateBook.approved_by,
        OfficialRateBook.approved_at,
        OfficialRateBook.effective_from,
        OfficialRateBook.effective_to,
        OfficialRateBook.activation_status,
        OfficialRateBook.activated_by,
        OfficialRateBook.activated_at,
        OfficialRateBook.current_identity_key,
    )
    rate_bundle = Bundle(
        "rate",
        FeeRate.id,
        FeeRate.fee_code,
        FeeRate.fee_name,
        FeeRate.fee_type,
        FeeRate.currency,
        FeeRate.default_amount,
        FeeRate.enabled,
        FeeRate.calc_mode,
        FeeRate.allow_reduction,
        FeeRate.effective_from,
        FeeRate.effective_to,
        FeeRate.official_rate_book_id,
    )
    rows = transaction.execute(
        select(
            book_bundle,
            rate_bundle,
            cast(FeeRate.default_amount, String).label("raw_default_amount"),
        )
        .outerjoin(
            FeeRate,
            and_(
                FeeRate.official_rate_book_id == OfficialRateBook.id,
                FeeRate.fee_code.in_(required_codes),
            ),
        )
        .where(
            OfficialRateBook.source_authority == "CNIPA",
            OfficialRateBook.effective_from <= rate_effective_on,
            or_(
                OfficialRateBook.effective_to.is_(None),
                OfficialRateBook.effective_to >= rate_effective_on,
            ),
        )
        .order_by(OfficialRateBook.id, FeeRate.fee_code, FeeRate.id)
    ).all()
    first_code = required_rates[0].fee_code
    if not rows:
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_MISSING,
            _provider_rate_details(first_code, rate_effective_on),
        )
    books = {row.book.id: _ProviderBook(*row.book) for row in rows}
    if len(books) != 1:
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
            _provider_rate_details(first_code, rate_effective_on),
        )
    book = next(iter(books.values()))
    if book.approval_status != "APPROVED" or book.activation_status != "ACTIVE":
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_UNAPPROVED,
            {"fee_code": first_code, "fee_year_key": 0, "rate_id": None},
        )
    invalid_field = _provider_book_invalid_field(book)
    if invalid_field is not None:
        _provider_raise(
            FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
            {"fee_code": first_code, "fee_year_key": 0, "field": invalid_field},
        )

    linked_rows = [
        (_ProviderRate(*row.rate), row.raw_default_amount)
        for row in rows
        if row.rate.id is not None
    ]
    selected: list[tuple[_RequiredRate, _ProviderRate, Decimal]] = []
    for required in required_rates:
        same_code = [item for item in linked_rows if item[0].fee_code == required.fee_code]
        for row, _raw_amount in same_code:
            invalid_interval_field = None
            if type(row.effective_from) is not date:
                invalid_interval_field = "effective_from"
            elif row.effective_to is not None and type(row.effective_to) is not date:
                invalid_interval_field = "effective_to"
            elif row.effective_to is not None and row.effective_to < row.effective_from:
                invalid_interval_field = "effective_to"
            if invalid_interval_field is not None:
                _provider_raise(
                    FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
                    {
                        "fee_code": required.fee_code,
                        "fee_year_key": 0,
                        "field": invalid_interval_field,
                    },
                )
        effective = [
            item
            for item in same_code
            for row in (item[0],)
            if row.effective_from <= rate_effective_on
            and (row.effective_to is None or rate_effective_on <= row.effective_to)
        ]
        matching = [
            item
            for item in effective
            for row in (item[0],)
            if row.fee_type == "GOV" and row.currency == "CNY" and row.enabled is True
        ]
        if not matching:
            _provider_raise(
                FeeEstimatePreviewErrorCode.RATE_MISSING,
                _provider_rate_details(required.fee_code, rate_effective_on),
            )
        if len(matching) != 1:
            _provider_raise(
                FeeEstimatePreviewErrorCode.RATE_SOURCE_AMBIGUOUS,
                _provider_rate_details(required.fee_code, rate_effective_on),
            )
        rate, raw_default_amount = matching[0]
        if rate.official_rate_book_id != book.id:
            _provider_raise(
                FeeEstimatePreviewErrorCode.RATE_SOURCE_INVALID,
                {
                    "fee_code": required.fee_code,
                    "fee_year_key": 0,
                    "field": "official_rate_book_id",
                },
            )
        selected.append(
            (
                required,
                rate,
                _provider_rate_amount(rate, required, raw_default_amount),
            )
        )
    return book, tuple(selected)


def _provider_valid_approval_snapshot(
    row: _ProviderApproval,
    *,
    case_id: str,
    ratio: Decimal,
) -> frozenset[str] | None:
    if not _exact_string(row.id) or row.scope_type != "CASE" or row.case_id != case_id:
        return None
    if row.applicant_set_key is not None or row.reduction_ratio != ratio:
        return None
    if row.confirmation_status != "CONFIRMED":
        return None
    if type(row.confirmed_at) is not datetime or not _exact_string(row.confirmed_by):
        return None
    if not _exact_string(row.source_evidence_version_id):
        return None
    if row.fee_year_from is not None or row.fee_year_to is not None:
        return None
    if type(row.effective_from) is not date:
        return None
    if row.effective_to is not None and type(row.effective_to) is not date:
        return None
    if row.effective_to is not None and row.effective_to < row.effective_from:
        return None
    fee_scope = _provider_canonical_json(row.fee_scope_snapshot)
    if type(fee_scope) is not dict or set(fee_scope) != {"fee_codes", "schema"}:
        return None
    if fee_scope["schema"] != _FEE_SCOPE_SCHEMA:
        return None
    fee_codes = fee_scope["fee_codes"]
    if (
        type(fee_codes) is not list
        or not fee_codes
        or any(not _exact_string(code) for code in fee_codes)
        or fee_codes != sorted(set(fee_codes))
    ):
        return None
    if (
        not _valid_sha256(row.fee_scope_hash)
        or _provider_digest(row.fee_scope_snapshot) != row.fee_scope_hash
    ):
        return None
    eligibility = _provider_canonical_json(row.eligibility_snapshot)
    if type(eligibility) is not dict or set(eligibility) != {
        "applicants",
        "attributes_version",
        "schema",
    }:
        return None
    if eligibility["schema"] != _ELIGIBILITY_SCHEMA or not _exact_string(
        eligibility["attributes_version"]
    ):
        return None
    applicants = eligibility["applicants"]
    if type(applicants) is not list or not applicants:
        return None
    applicant_ids: list[str] = []
    for applicant in applicants:
        if type(applicant) is not dict or set(applicant) != {"applicant_id", "attributes"}:
            return None
        if (
            not _exact_string(applicant["applicant_id"])
            or type(applicant["attributes"]) is not dict
        ):
            return None
        applicant_ids.append(applicant["applicant_id"])
    if applicant_ids != sorted(set(applicant_ids)):
        return None
    if (
        not _valid_sha256(row.eligibility_snapshot_hash)
        or _provider_digest(row.eligibility_snapshot) != row.eligibility_snapshot_hash
        or not _valid_sha256(row.approval_identity_key)
    ):
        return None
    return frozenset(fee_codes)


def _provider_approvals(
    transaction: Session,
    *,
    case_id: str,
    ratio: Decimal,
    rate_effective_on: date,
    fee_codes: tuple[str, ...],
) -> dict[str, FeeReductionApprovalContext]:
    approval_bundle = Bundle(
        "approval",
        FeeReductionApproval.id,
        FeeReductionApproval.scope_type,
        FeeReductionApproval.case_id,
        FeeReductionApproval.applicant_set_key,
        FeeReductionApproval.reduction_ratio,
        FeeReductionApproval.fee_scope_snapshot,
        FeeReductionApproval.fee_scope_hash,
        FeeReductionApproval.fee_year_from,
        FeeReductionApproval.fee_year_to,
        FeeReductionApproval.effective_from,
        FeeReductionApproval.effective_to,
        FeeReductionApproval.source_evidence_version_id,
        FeeReductionApproval.confirmation_status,
        FeeReductionApproval.confirmed_at,
        FeeReductionApproval.confirmed_by,
        FeeReductionApproval.eligibility_snapshot,
        FeeReductionApproval.eligibility_snapshot_hash,
        FeeReductionApproval.approval_identity_key,
    )
    rows = transaction.execute(
        select(approval_bundle)
        .where(
            FeeReductionApproval.scope_type == "CASE",
            FeeReductionApproval.case_id == case_id,
            FeeReductionApproval.reduction_ratio == ratio,
            FeeReductionApproval.confirmation_status == "CONFIRMED",
            FeeReductionApproval.effective_from <= rate_effective_on,
            or_(
                FeeReductionApproval.effective_to.is_(None),
                FeeReductionApproval.effective_to >= rate_effective_on,
            ),
        )
        .order_by(FeeReductionApproval.id)
    ).all()
    parsed: list[tuple[_ProviderApproval, frozenset[str]]] = []
    for result_row in rows:
        row = _ProviderApproval(*result_row.approval)
        scope = _provider_valid_approval_snapshot(row, case_id=case_id, ratio=ratio)
        if scope is None:
            _provider_candidate_invalid(fee_codes[0], "reduction_approval")
        parsed.append((row, scope))

    result: dict[str, FeeReductionApprovalContext] = {}
    for fee_code in fee_codes:
        applicable = [(row, scope) for row, scope in parsed if fee_code in scope]
        if len(applicable) != 1:
            _provider_candidate_invalid(fee_code, "reduction_approval")
        row, scope = applicable[0]
        result[fee_code] = FeeReductionApprovalContext(
            approval_id=row.id,
            scope_type=FeeReductionApprovalScopeType.CASE,
            case_id=row.case_id,
            applicant_set_key=None,
            reduction_ratio=row.reduction_ratio,
            fee_codes=scope,
            fee_year_from=None,
            fee_year_to=None,
            effective_from=row.effective_from,
            effective_to=row.effective_to,
            source_evidence_version_id=row.source_evidence_version_id,
            confirmation_status=row.confirmation_status,
            is_current=True,
        )
    return result


class SqlAlchemyOfficialFeeEstimateRateProvider:
    def __init__(self, transaction: Session) -> None:
        self._transaction = transaction

    def select_rate_candidates(
        self,
        *,
        command: PreviewFeeEstimateCommand,
        rate_effective_on: date,
    ) -> tuple[OfficialFeeEstimateRateCandidate, ...]:
        trigger = command.trigger_context.trigger
        if type(trigger) is not str or trigger not in _PROVIDER_SUPPORTED_TRIGGERS:
            _provider_raise(
                FeeEstimatePreviewErrorCode.TRIGGER_UNSUPPORTED,
                {"trigger": trigger},
            )
        if type(command.currency) is not str or command.currency != "CNY":
            _provider_raise(FeeEstimatePreviewErrorCode.INVALID_COMMAND, {"field": "currency"})
        if type(rate_effective_on) is not date:
            _provider_raise(
                FeeEstimatePreviewErrorCode.INVALID_COMMAND,
                {"field": "rate_effective_on"},
            )

        with self._transaction.no_autoflush:
            case, required_rates = _provider_case_facts(self._transaction, command, trigger)
            book, selected = _provider_rate_rows(
                self._transaction,
                required_rates,
                rate_effective_on,
            )
            approval_codes = tuple(
                required.fee_code
                for required, row, _amount in selected
                if row.allow_reduction is True and case.fee_reduction != Decimal("0")
            )
            approvals = (
                _provider_approvals(
                    self._transaction,
                    case_id=case.id,
                    ratio=case.fee_reduction,
                    rate_effective_on=rate_effective_on,
                    fee_codes=approval_codes,
                )
                if approval_codes
                else {}
            )

        return tuple(
            OfficialFeeEstimateRateCandidate(
                fee_code=required.fee_code,
                fee_name=row.fee_name,
                fee_year_key=0,
                official_full_amount=amount,
                source=FeeEstimateSource(
                    rate_id=row.id,
                    source_document_id=command.trigger_context.source_document_id,
                    source_doc=book.source_version,
                    source_url=book.source_reference,
                    source_policy=book.book_code,
                    source_version=book.version_code,
                    status=FeeSourceStatus.VERIFIED,
                ),
                reduction_input=FeeReductionInput(
                    reduction_ratio=(
                        case.fee_reduction if row.allow_reduction is True else Decimal("0")
                    ),
                    provenance=FeeReductionInputProvenance.EXPLICIT_ENTRY,
                ),
                reduction_context=FeeReductionEvaluationContext(
                    case_id=case.id,
                    applicant_set_key=None,
                    fee_code=required.fee_code,
                    fee_year_key=0,
                    as_of_date=rate_effective_on,
                ),
                reduction_approval=approvals.get(required.fee_code),
            )
            for required, row, amount in selected
        )


_LAYOUT_FEE_CODE = "IC_LAYOUT_REGISTRATION_FEE"
_LAYOUT_BOOK_CODE = "CNIPA_LAYOUT_246"
_LAYOUT_VERSION = "2017-07-01"
_LAYOUT_EFFECTIVE_FROM = date(2017, 7, 1)
_LAYOUT_SOURCE_REFERENCE = "https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html"
_LAYOUT_SOURCE_PUBLISHED_ON = date(2017, 6, 30)
_LAYOUT_SOURCE_SNAPSHOT_HASH = "f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4"
_LAYOUT_SOURCE_TITLE = "关于执行新的集成电路布图设计保护费收费标准的公告（第246号）"
_LAYOUT_DOCUMENT_NUMBER = "第二四六号"
_LAYOUT_AMOUNT = Decimal("1000.00")
_LAYOUT_REEXAMINATION_FEE_CODE = "IC_LAYOUT_REEXAM_REQUEST_FEE"
_LAYOUT_REEXAMINATION_AMOUNT = Decimal("1000.00")
_LAYOUT_RESTORATION_FEE_CODE = "IC_LAYOUT_RESTORATION_REQUEST_FEE"
_LAYOUT_RESTORATION_AMOUNT = Decimal("500.00")
_LAYOUT_BIBLIOGRAPHIC_CHANGE_FEE_CODE = "IC_LAYOUT_BIBLIOGRAPHIC_CHANGE_FEE"
_LAYOUT_BIBLIOGRAPHIC_CHANGE_AMOUNT = Decimal("50.00")
_LAYOUT_EXTENSION_FEE_CODE = "IC_LAYOUT_EXTENSION_REQUEST_FEE"
_LAYOUT_EXTENSION_AMOUNT = Decimal("150.00")
_LAYOUT_NONVOLUNTARY_LICENSE_FEE_CODE = "IC_LAYOUT_NONVOLUNTARY_LICENSE_REQUEST_FEE"
_LAYOUT_NONVOLUNTARY_LICENSE_AMOUNT = Decimal("150.00")
_LAYOUT_REMUNERATION_ADJUDICATION_FEE_CODE = (
    "IC_LAYOUT_NONVOLUNTARY_LICENSE_REMUNERATION_ADJUDICATION_FEE"
)
_LAYOUT_REMUNERATION_ADJUDICATION_AMOUNT = Decimal("150.00")
_PATENT_TERM_COMPENSATION_REQUEST_FEE_CODE = "CN_PATENT_TERM_COMPENSATION_REQUEST_FEE"
_PATENT_TERM_COMPENSATION_REQUEST_FEE_AMOUNT = Decimal("200.00")
_PATENT_TERM_COMPENSATION_REQUEST_FEE_EFFECTIVE_FROM = date(2024, 8, 6)
_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_REFERENCE = (
    "CNIPA_ANNOUNCEMENT_594_AND_PAYMENT_GUIDE_20260330"
)
_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_VERSION = "2024-08-06/2026-03-30"
_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_SNAPSHOT_HASH = (
    "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544"
)
_COMPENSATION_PERIOD_ANNUITY_FEE_CODE = "CN_COMPENSATION_PERIOD_ANNUITY_FEE"
_COMPENSATION_PERIOD_ANNUITY_FEE_UNIT_AMOUNT = Decimal("8000.00")
_COMPENSATION_PERIOD_ANNUITY_FEE_EFFECTIVE_FROM = date(2024, 7, 26)
_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_REFERENCE = (
    "NDRC_2024_1156_CNIPA_594_PAYMENT_NOTICE_AND_GUIDE_20260330"
)
_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_VERSION = "2024-07-26/2024-08-06/2026-03-30"
_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_SNAPSHOT_HASH = (
    "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544"
)
_OPEN_LICENSE_ANNUITY_REDUCTION_RATIO = Decimal("0.15")


@dataclass(frozen=True, slots=True)
class _LayoutRate:
    id: str
    fee_code: str
    fee_type: str
    currency: str
    default_amount: Decimal | None
    enabled: bool
    calc_mode: str | None
    allow_reduction: bool | None
    effective_from: date | None
    effective_to: date | None
    source_doc: str | None
    source_url: str | None
    source_policy: str | None
    source_version: str | None
    source_status: str | None
    official_rate_book_id: str | None


def _layout_invalid(field: str) -> None:
    _fail(
        "LAYOUT_REGISTRATION_FEE_INVALID_INPUT",
        "Invalid layout registration fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_unavailable(field: str) -> None:
    _fail(
        "LAYOUT_REGISTRATION_FEE_UNAVAILABLE",
        "The authoritative layout registration fee is unavailable",
        status_code=409,
        details={"field": field},
    )


def _layout_reexamination_invalid(field: str) -> None:
    _fail(
        "LAYOUT_REEXAMINATION_FEE_INVALID_INPUT",
        "Invalid layout reexamination fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_restoration_invalid(field: str) -> None:
    _fail(
        "LAYOUT_RESTORATION_FEE_INVALID_INPUT",
        "Invalid layout restoration fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_bibliographic_change_invalid(field: str) -> None:
    _fail(
        "LAYOUT_BIBLIOGRAPHIC_CHANGE_FEE_INVALID_INPUT",
        "Invalid layout bibliographic change fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_extension_invalid(field: str) -> None:
    _fail(
        "LAYOUT_EXTENSION_FEE_INVALID_INPUT",
        "Invalid layout extension fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_nonvoluntary_license_invalid(field: str) -> None:
    _fail(
        "LAYOUT_NONVOLUNTARY_LICENSE_FEE_INVALID_INPUT",
        "Invalid layout nonvoluntary license fee command",
        status_code=400,
        details={"field": field},
    )


def _layout_remuneration_adjudication_invalid(field: str) -> None:
    _fail(
        "LAYOUT_REMUNERATION_ADJUDICATION_FEE_INVALID_INPUT",
        "Invalid layout remuneration adjudication fee command",
        status_code=400,
        details={"field": field},
    )


def _patent_term_compensation_request_fee_invalid() -> None:
    _fail(
        "PATENT_TERM_COMPENSATION_REQUEST_FEE_INVALID_INPUT",
        "Invalid patent term compensation request fee command",
        status_code=400,
        details={"field": "effective_date"},
    )


def _patent_term_compensation_request_fee_unavailable(effective_date: date) -> None:
    _fail(
        "PATENT_TERM_COMPENSATION_REQUEST_FEE_UNAVAILABLE",
        "The patent term compensation request fee is unavailable",
        status_code=400,
        details={
            "effective_date": effective_date.isoformat(),
            "effective_from": (_PATENT_TERM_COMPENSATION_REQUEST_FEE_EFFECTIVE_FROM.isoformat()),
        },
    )


def _compensation_period_annuity_fee_invalid(field: str) -> None:
    _fail(
        "COMPENSATION_PERIOD_ANNUITY_FEE_INVALID_INPUT",
        "Invalid compensation period annuity fee command",
        status_code=400,
        details={"field": field},
    )


def _compensation_period_annuity_fee_unavailable(effective_date: date) -> None:
    _fail(
        "COMPENSATION_PERIOD_ANNUITY_FEE_UNAVAILABLE",
        "The compensation period annuity fee is unavailable",
        status_code=400,
        details={
            "effective_date": effective_date.isoformat(),
            "effective_from": _COMPENSATION_PERIOD_ANNUITY_FEE_EFFECTIVE_FROM.isoformat(),
        },
    )


def _open_license_annuity_reduction_invalid(field: str) -> None:
    _fail(
        "OPEN_LICENSE_ANNUITY_REDUCTION_INVALID_INPUT",
        "Invalid open-license annuity reduction command",
        status_code=400,
        details={"field": field},
    )


def _layout_date(
    value: object,
    field: str,
    *,
    optional: bool = False,
    unavailable: Callable[[str], None] = _layout_unavailable,
) -> date | None:
    if value is None and optional:
        return None
    if type(value) is not str:
        unavailable(field)
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        unavailable(field)
    if parsed.isoformat() != value:
        unavailable(field)
    return parsed


def _layout_datetime(
    value: object,
    field: str,
    *,
    unavailable: Callable[[str], None] = _layout_unavailable,
) -> datetime:
    if type(value) is not str:
        unavailable(field)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        unavailable(field)
    if parsed.utcoffset() is not None:
        unavailable(field)
    return parsed


def _layout_canonical_uuid(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        return str(UUID(value)) == value
    except (AttributeError, TypeError, ValueError):
        return False


def _layout_book(
    transaction: Session,
    effective_date: date,
    *,
    unavailable: Callable[[str], None] = _layout_unavailable,
) -> _ProviderBook:
    book_bundle = Bundle(
        "book",
        OfficialRateBook.id,
        OfficialRateBook.book_code,
        OfficialRateBook.version_code,
        OfficialRateBook.source_authority,
        OfficialRateBook.source_reference,
        OfficialRateBook.source_version,
        cast(OfficialRateBook.source_published_on, String).label("source_published_on"),
        OfficialRateBook.source_snapshot,
        OfficialRateBook.source_snapshot_hash,
        OfficialRateBook.approval_status,
        OfficialRateBook.approved_by,
        cast(OfficialRateBook.approved_at, String).label("approved_at"),
        cast(OfficialRateBook.effective_from, String).label("effective_from"),
        cast(OfficialRateBook.effective_to, String).label("effective_to"),
        OfficialRateBook.activation_status,
        OfficialRateBook.activated_by,
        cast(OfficialRateBook.activated_at, String).label("activated_at"),
        OfficialRateBook.current_identity_key,
    )
    rows = transaction.execute(
        select(book_bundle)
        .where(
            OfficialRateBook.source_authority == "CNIPA",
            OfficialRateBook.book_code == _LAYOUT_BOOK_CODE,
            OfficialRateBook.version_code == _LAYOUT_VERSION,
            OfficialRateBook.effective_from == _LAYOUT_EFFECTIVE_FROM,
            OfficialRateBook.effective_to.is_(None),
            OfficialRateBook.approval_status == "APPROVED",
            OfficialRateBook.activation_status == "ACTIVE",
            OfficialRateBook.effective_from <= effective_date,
            or_(
                OfficialRateBook.effective_to.is_(None),
                OfficialRateBook.effective_to >= effective_date,
            ),
        )
        .order_by(OfficialRateBook.id)
    ).all()
    if len(rows) != 1:
        unavailable("rate_book")
    raw = rows[0].book
    book = _ProviderBook(
        id=raw.id,
        book_code=raw.book_code,
        version_code=raw.version_code,
        source_authority=raw.source_authority,
        source_reference=raw.source_reference,
        source_version=raw.source_version,
        source_published_on=_layout_date(
            raw.source_published_on,
            "source_published_on",
            unavailable=unavailable,
        ),
        source_snapshot=raw.source_snapshot,
        source_snapshot_hash=raw.source_snapshot_hash,
        approval_status=raw.approval_status,
        approved_by=raw.approved_by,
        approved_at=_layout_datetime(
            raw.approved_at,
            "approved_at",
            unavailable=unavailable,
        ),
        effective_from=_layout_date(
            raw.effective_from,
            "effective_from",
            unavailable=unavailable,
        ),
        effective_to=_layout_date(
            raw.effective_to,
            "effective_to",
            optional=True,
            unavailable=unavailable,
        ),
        activation_status=raw.activation_status,
        activated_by=raw.activated_by,
        activated_at=_layout_datetime(
            raw.activated_at,
            "activated_at",
            unavailable=unavailable,
        ),
        current_identity_key=raw.current_identity_key,
    )
    invalid_field = _provider_book_invalid_field(book)
    if invalid_field is not None:
        unavailable(invalid_field)
    for field in ("id", "approved_by", "activated_by"):
        if not _layout_canonical_uuid(getattr(book, field)):
            unavailable(field)
    if book.approved_at > book.activated_at:
        unavailable("approved_at/activated_at")
    exact_values = (
        ("source_reference", book.source_reference, _LAYOUT_SOURCE_REFERENCE),
        ("source_version", book.source_version, _LAYOUT_VERSION),
        ("source_published_on", book.source_published_on, _LAYOUT_SOURCE_PUBLISHED_ON),
        ("source_snapshot_hash", book.source_snapshot_hash, _LAYOUT_SOURCE_SNAPSHOT_HASH),
        ("approval_status", book.approval_status, "APPROVED"),
        ("activation_status", book.activation_status, "ACTIVE"),
        ("current_identity_key", book.current_identity_key, f"CNIPA|{_LAYOUT_BOOK_CODE}"),
    )
    for field, value, expected in exact_values:
        if value != expected:
            unavailable(field)
    return book


def _layout_rate(
    transaction: Session,
    book: _ProviderBook,
) -> _LayoutRate:
    rate_bundle = Bundle(
        "rate",
        FeeRate.id,
        FeeRate.fee_code,
        FeeRate.fee_type,
        FeeRate.currency,
        cast(FeeRate.default_amount, String).label("default_amount"),
        cast(FeeRate.enabled, String).label("enabled"),
        FeeRate.calc_mode,
        cast(FeeRate.allow_reduction, String).label("allow_reduction"),
        cast(FeeRate.effective_from, String).label("effective_from"),
        cast(FeeRate.effective_to, String).label("effective_to"),
        FeeRate.source_doc,
        FeeRate.source_url,
        FeeRate.source_policy,
        FeeRate.source_version,
        FeeRate.source_status,
        FeeRate.official_rate_book_id,
    )
    rows = transaction.execute(
        select(
            rate_bundle,
        )
        .where(
            FeeRate.official_rate_book_id == book.id,
            FeeRate.fee_code == _LAYOUT_FEE_CODE,
        )
        .order_by(FeeRate.id)
    ).all()
    if len(rows) != 1:
        _layout_unavailable("rate")
    raw = rows[0].rate
    try:
        stored_amount = Decimal(raw.default_amount)
    except (InvalidOperation, TypeError, ValueError):
        _layout_unavailable("default_amount")
    if raw.enabled != "1":
        _layout_unavailable("enabled")
    if raw.allow_reduction != "0":
        _layout_unavailable("allow_reduction")
    rate = _LayoutRate(
        id=raw.id,
        fee_code=raw.fee_code,
        fee_type=raw.fee_type,
        currency=raw.currency,
        default_amount=stored_amount,
        enabled=True,
        calc_mode=raw.calc_mode,
        allow_reduction=False,
        effective_from=_layout_date(raw.effective_from, "effective_from"),
        effective_to=_layout_date(raw.effective_to, "effective_to", optional=True),
        source_doc=raw.source_doc,
        source_url=raw.source_url,
        source_policy=raw.source_policy,
        source_version=raw.source_version,
        source_status=raw.source_status,
        official_rate_book_id=raw.official_rate_book_id,
    )
    exact_values = (
        ("id", rate.id, rate.id if _layout_canonical_uuid(rate.id) else None),
        ("fee_code", rate.fee_code, _LAYOUT_FEE_CODE),
        ("fee_type", rate.fee_type, "GOV"),
        ("currency", rate.currency, "CNY"),
        ("enabled", rate.enabled, True),
        ("calc_mode", rate.calc_mode, "FIXED"),
        ("allow_reduction", rate.allow_reduction, False),
        ("effective_from", rate.effective_from, _LAYOUT_EFFECTIVE_FROM),
        ("effective_to", rate.effective_to, None),
        ("source_doc", rate.source_doc, _LAYOUT_SOURCE_TITLE),
        ("source_url", rate.source_url, _LAYOUT_SOURCE_REFERENCE),
        ("source_policy", rate.source_policy, _LAYOUT_DOCUMENT_NUMBER),
        ("source_version", rate.source_version, _LAYOUT_VERSION),
        ("source_status", rate.source_status, "PENDING_CONFIRMATION"),
        ("official_rate_book_id", rate.official_rate_book_id, book.id),
    )
    for field, value, expected in exact_values:
        if value != expected:
            _layout_unavailable(field)
    if (
        type(rate.default_amount) is not Decimal
        or not rate.default_amount.is_finite()
        or rate.default_amount != _LAYOUT_AMOUNT
        or not stored_amount.is_finite()
        or stored_amount != _LAYOUT_AMOUNT
        or stored_amount != stored_amount.quantize(_PROVIDER_TWO_PLACES)
    ):
        _layout_unavailable("default_amount")
    return rate


def get_layout_registration_fee(
    command: GetLayoutRegistrationFeeCommand,
    transaction: Session,
) -> GetLayoutRegistrationFeeResult:
    if type(command) is not GetLayoutRegistrationFeeCommand:
        _layout_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_invalid("effective_date")
    if not isinstance(transaction, Session):
        _layout_invalid("transaction")

    with transaction.no_autoflush:
        book = _layout_book(transaction, command.effective_date)
        rate = _layout_rate(transaction, book)

    return GetLayoutRegistrationFeeResult(
        rate_id=rate.id,
        fee_code=rate.fee_code,
        fee_type=rate.fee_type,
        currency=rate.currency,
        calc_mode=rate.calc_mode,
        allow_reduction=rate.allow_reduction,
        enabled=rate.enabled,
        amount=rate.default_amount,
        rate_book_id=book.id,
        book_code=book.book_code,
        version_code=book.version_code,
        effective_from=book.effective_from,
        effective_to=book.effective_to,
        approval_status=book.approval_status,
        activation_status=book.activation_status,
        source_reference=book.source_reference,
        source_version=book.source_version,
        source_snapshot_hash=book.source_snapshot_hash,
    )


def get_layout_bibliographic_change_fee(
    command: GetLayoutBibliographicChangeFeeCommand,
) -> GetLayoutBibliographicChangeFeeResult:
    if type(command) is not GetLayoutBibliographicChangeFeeCommand:
        _layout_bibliographic_change_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_bibliographic_change_invalid("effective_date")

    return GetLayoutBibliographicChangeFeeResult(
        fee_code=_LAYOUT_BIBLIOGRAPHIC_CHANGE_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_BIBLIOGRAPHIC_CHANGE_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )


def get_layout_extension_fee(
    command: GetLayoutExtensionFeeCommand,
) -> GetLayoutExtensionFeeResult:
    if type(command) is not GetLayoutExtensionFeeCommand:
        _layout_extension_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_extension_invalid("effective_date")

    return GetLayoutExtensionFeeResult(
        fee_code=_LAYOUT_EXTENSION_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_EXTENSION_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )


def get_layout_nonvoluntary_license_fee(
    command: GetLayoutNonvoluntaryLicenseFeeCommand,
) -> GetLayoutNonvoluntaryLicenseFeeResult:
    if type(command) is not GetLayoutNonvoluntaryLicenseFeeCommand:
        _layout_nonvoluntary_license_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_nonvoluntary_license_invalid("effective_date")

    return GetLayoutNonvoluntaryLicenseFeeResult(
        fee_code=_LAYOUT_NONVOLUNTARY_LICENSE_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_NONVOLUNTARY_LICENSE_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )


def get_layout_remuneration_adjudication_fee(
    command: GetLayoutRemunerationAdjudicationFeeCommand,
) -> GetLayoutRemunerationAdjudicationFeeResult:
    if type(command) is not GetLayoutRemunerationAdjudicationFeeCommand:
        _layout_remuneration_adjudication_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_remuneration_adjudication_invalid("effective_date")

    return GetLayoutRemunerationAdjudicationFeeResult(
        fee_code=_LAYOUT_REMUNERATION_ADJUDICATION_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_REMUNERATION_ADJUDICATION_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )


def get_patent_term_compensation_request_fee(
    command: GetPatentTermCompensationRequestFeeCommand,
) -> GetPatentTermCompensationRequestFeeResult:
    if type(command) is not GetPatentTermCompensationRequestFeeCommand:
        _patent_term_compensation_request_fee_invalid()
    if type(command.effective_date) is not date:
        _patent_term_compensation_request_fee_invalid()
    if command.effective_date < _PATENT_TERM_COMPENSATION_REQUEST_FEE_EFFECTIVE_FROM:
        _patent_term_compensation_request_fee_unavailable(command.effective_date)

    return GetPatentTermCompensationRequestFeeResult(
        fee_code=_PATENT_TERM_COMPENSATION_REQUEST_FEE_CODE,
        currency="CNY",
        amount=_PATENT_TERM_COMPENSATION_REQUEST_FEE_AMOUNT,
        effective_from=_PATENT_TERM_COMPENSATION_REQUEST_FEE_EFFECTIVE_FROM,
        source_reference=_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_REFERENCE,
        source_version=_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_VERSION,
        source_snapshot_hash=(_PATENT_TERM_COMPENSATION_REQUEST_FEE_SOURCE_SNAPSHOT_HASH),
    )


def calculate_compensation_period_annuity_fee(
    command: CalculateCompensationPeriodAnnuityFeeCommand,
) -> CalculateCompensationPeriodAnnuityFeeResult:
    if type(command) is not CalculateCompensationPeriodAnnuityFeeCommand:
        _compensation_period_annuity_fee_invalid("command")
    if type(command.effective_date) is not date:
        _compensation_period_annuity_fee_invalid("effective_date")
    if type(command.complete_years) is not int or command.complete_years < 0:
        _compensation_period_annuity_fee_invalid("complete_years")
    if command.effective_date < _COMPENSATION_PERIOD_ANNUITY_FEE_EFFECTIVE_FROM:
        _compensation_period_annuity_fee_unavailable(command.effective_date)

    return CalculateCompensationPeriodAnnuityFeeResult(
        fee_code=_COMPENSATION_PERIOD_ANNUITY_FEE_CODE,
        currency="CNY",
        complete_years=command.complete_years,
        unit_amount=_COMPENSATION_PERIOD_ANNUITY_FEE_UNIT_AMOUNT,
        amount=_COMPENSATION_PERIOD_ANNUITY_FEE_UNIT_AMOUNT * command.complete_years,
        effective_from=_COMPENSATION_PERIOD_ANNUITY_FEE_EFFECTIVE_FROM,
        source_reference=_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_REFERENCE,
        source_version=_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_VERSION,
        source_snapshot_hash=(_COMPENSATION_PERIOD_ANNUITY_FEE_SOURCE_SNAPSHOT_HASH),
    )


def calculate_open_license_annuity_reduction(
    command: CalculateOpenLicenseAnnuityReductionCommand,
) -> CalculateOpenLicenseAnnuityReductionResult:
    if type(command) is not CalculateOpenLicenseAnnuityReductionCommand:
        _open_license_annuity_reduction_invalid("command")
    existing_reduction_ratio = command.existing_reduction_ratio
    if (
        type(existing_reduction_ratio) is not Decimal
        or not existing_reduction_ratio.is_finite()
        or existing_reduction_ratio not in (Decimal("0"), Decimal("0.7"), Decimal("0.85"))
    ):
        _open_license_annuity_reduction_invalid("existing_reduction_ratio")

    applied_reduction_ratio = max(
        _OPEN_LICENSE_ANNUITY_REDUCTION_RATIO,
        existing_reduction_ratio,
    )
    return CalculateOpenLicenseAnnuityReductionResult(
        open_license_reduction_ratio=_OPEN_LICENSE_ANNUITY_REDUCTION_RATIO,
        existing_reduction_ratio=existing_reduction_ratio,
        applied_reduction_ratio=applied_reduction_ratio,
        payable_ratio=Decimal("1") - applied_reduction_ratio,
    )


def get_layout_reexamination_fee(
    command: GetLayoutReexaminationFeeCommand,
) -> GetLayoutReexaminationFeeResult:
    if type(command) is not GetLayoutReexaminationFeeCommand:
        _layout_reexamination_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_reexamination_invalid("effective_date")

    return GetLayoutReexaminationFeeResult(
        fee_code=_LAYOUT_REEXAMINATION_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_REEXAMINATION_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )


def get_layout_restoration_fee(
    command: GetLayoutRestorationFeeCommand,
) -> GetLayoutRestorationFeeResult:
    if type(command) is not GetLayoutRestorationFeeCommand:
        _layout_restoration_invalid("command")
    if type(command.effective_date) is not date or command.effective_date < _LAYOUT_EFFECTIVE_FROM:
        _layout_restoration_invalid("effective_date")

    return GetLayoutRestorationFeeResult(
        fee_code=_LAYOUT_RESTORATION_FEE_CODE,
        currency="CNY",
        amount=_LAYOUT_RESTORATION_AMOUNT,
        effective_from=_LAYOUT_EFFECTIVE_FROM,
        source_reference=_LAYOUT_SOURCE_REFERENCE,
        source_version=_LAYOUT_VERSION,
        source_snapshot_hash=_LAYOUT_SOURCE_SNAPSHOT_HASH,
    )
