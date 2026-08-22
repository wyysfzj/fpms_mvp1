from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import MAX_EMAX, MIN_EMIN, ROUND_HALF_UP, Decimal, localcontext
from enum import Enum

__all__ = (
    "AnnuityLateFeeCalculationSource",
    "AnnuityLateFeeErrorCode",
    "AnnuityLateFeeNotificationBand",
    "CalculateAnnuityLateFeeCommand",
    "AnnuityLateFeeResult",
    "AnnuityLateFeeRuleError",
    "calculate_annuity_late_fee",
)


class AnnuityLateFeeCalculationSource(str, Enum):
    STATUTORY = "STATUTORY"
    NOTIFICATION = "NOTIFICATION"


class AnnuityLateFeeErrorCode(str, Enum):
    INVALID_FULL_ANNUAL_FEE = "INVALID_FULL_ANNUAL_FEE"
    PAYMENT_BEFORE_DUE_DATE = "PAYMENT_BEFORE_DUE_DATE"
    PAYMENT_AFTER_LATE_WINDOW = "PAYMENT_AFTER_LATE_WINDOW"
    INVALID_NOTIFICATION_BAND = "INVALID_NOTIFICATION_BAND"
    NOTIFICATION_BAND_OVERLAP = "NOTIFICATION_BAND_OVERLAP"
    NOTIFICATION_BAND_GAP = "NOTIFICATION_BAND_GAP"


@dataclass(frozen=True, slots=True)
class AnnuityLateFeeNotificationBand:
    start_date: date
    end_date: date
    rate: Decimal
    amount: Decimal
    source_document_id: str


@dataclass(frozen=True, slots=True)
class CalculateAnnuityLateFeeCommand:
    full_annual_fee: Decimal
    statutory_due_date: date
    payment_date: date
    notification_bands: tuple[AnnuityLateFeeNotificationBand, ...] = ()


@dataclass(frozen=True, slots=True)
class AnnuityLateFeeResult:
    full_annual_fee: Decimal
    statutory_due_date: date
    payment_date: date
    rate: Decimal
    late_fee_amount: Decimal
    band_start_date: date
    band_end_date: date
    calculation_source: AnnuityLateFeeCalculationSource
    source_document_id: str | None


class AnnuityLateFeeRuleError(ValueError):
    def __init__(self, code: AnnuityLateFeeErrorCode) -> None:
        self._code = code
        super().__init__(code.value)

    @property
    def code(self) -> AnnuityLateFeeErrorCode:
        return self._code


_CENT = Decimal("0.01")
_RATES = (
    Decimal("0"),
    Decimal("0.05"),
    Decimal("0.10"),
    Decimal("0.15"),
    Decimal("0.20"),
    Decimal("0.25"),
)


def _raise(code: AnnuityLateFeeErrorCode) -> None:
    raise AnnuityLateFeeRuleError(code)


def _calendar_month_anniversary(original: date, months: int) -> date:
    month_index = original.month - 1 + months
    year = original.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(original.day, monthrange(year, month)[1]))


def _quantize_precision(value: Decimal) -> int:
    return max(len(value.as_tuple().digits), value.adjusted() + 3, 1)


def _quantize_cents(value: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = max(context.prec, _quantize_precision(value))
        context.Emax = MAX_EMAX
        context.Emin = MIN_EMIN
        return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _multiply_and_quantize_cents(left: Decimal, right: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = max(
            context.prec,
            len(left.as_tuple().digits) + len(right.as_tuple().digits),
        )
        context.Emax = MAX_EMAX
        context.Emin = MIN_EMIN
        product = left * right
        context.prec = max(context.prec, _quantize_precision(product))
        return product.quantize(_CENT, rounding=ROUND_HALF_UP)


def _statutory_band(
    statutory_due_date: date,
    payment_date: date,
) -> tuple[Decimal, date, date]:
    anniversaries = tuple(
        _calendar_month_anniversary(statutory_due_date, month) for month in range(7)
    )
    for index, rate in enumerate(_RATES[:-1]):
        band_end = anniversaries[index + 1] - timedelta(days=1)
        if payment_date <= band_end:
            return rate, anniversaries[index], band_end
    return _RATES[-1], anniversaries[5], anniversaries[6]


def _validate_notification_bands(
    notification_bands: tuple[AnnuityLateFeeNotificationBand, ...],
    statutory_due_date: date,
    late_window_end: date,
) -> tuple[AnnuityLateFeeNotificationBand, ...]:
    for band in notification_bands:
        if (
            not isinstance(band, AnnuityLateFeeNotificationBand)
            or type(band.start_date) is not date
            or type(band.end_date) is not date
            or band.start_date > band.end_date
            or band.start_date < statutory_due_date
            or band.end_date > late_window_end
            or not isinstance(band.rate, Decimal)
            or not band.rate.is_finite()
            or band.rate not in _RATES
            or not isinstance(band.amount, Decimal)
            or not band.amount.is_finite()
            or band.amount < 0
            or not isinstance(band.source_document_id, str)
            or not band.source_document_id.strip()
        ):
            _raise(AnnuityLateFeeErrorCode.INVALID_NOTIFICATION_BAND)

    sorted_bands = tuple(
        sorted(
            notification_bands,
            key=lambda band: (
                band.start_date,
                band.end_date,
                band.source_document_id,
            ),
        )
    )
    adjacent_pairs = tuple(zip(sorted_bands, sorted_bands[1:], strict=False))
    if any(current.start_date <= previous.end_date for previous, current in adjacent_pairs):
        _raise(AnnuityLateFeeErrorCode.NOTIFICATION_BAND_OVERLAP)
    if any(
        current.start_date != previous.end_date + timedelta(days=1)
        for previous, current in adjacent_pairs
    ):
        _raise(AnnuityLateFeeErrorCode.NOTIFICATION_BAND_GAP)
    return sorted_bands


def calculate_annuity_late_fee(command: CalculateAnnuityLateFeeCommand, /) -> AnnuityLateFeeResult:
    full_annual_fee = command.full_annual_fee
    if (
        not isinstance(full_annual_fee, Decimal)
        or not full_annual_fee.is_finite()
        or full_annual_fee <= 0
    ):
        _raise(AnnuityLateFeeErrorCode.INVALID_FULL_ANNUAL_FEE)

    statutory_due_date = command.statutory_due_date
    payment_date = command.payment_date
    late_window_end = _calendar_month_anniversary(statutory_due_date, 6)
    if payment_date < statutory_due_date:
        _raise(AnnuityLateFeeErrorCode.PAYMENT_BEFORE_DUE_DATE)
    if payment_date > late_window_end:
        _raise(AnnuityLateFeeErrorCode.PAYMENT_AFTER_LATE_WINDOW)

    statutory_rate, statutory_start, statutory_end = _statutory_band(
        statutory_due_date,
        payment_date,
    )
    notification_bands = _validate_notification_bands(
        command.notification_bands,
        statutory_due_date,
        late_window_end,
    )
    for band in notification_bands:
        if band.start_date <= payment_date <= band.end_date:
            return AnnuityLateFeeResult(
                full_annual_fee=full_annual_fee,
                statutory_due_date=statutory_due_date,
                payment_date=payment_date,
                rate=band.rate,
                late_fee_amount=_quantize_cents(band.amount),
                band_start_date=band.start_date,
                band_end_date=band.end_date,
                calculation_source=AnnuityLateFeeCalculationSource.NOTIFICATION,
                source_document_id=band.source_document_id,
            )

    if notification_bands and statutory_rate != 0:
        _raise(AnnuityLateFeeErrorCode.NOTIFICATION_BAND_GAP)

    return AnnuityLateFeeResult(
        full_annual_fee=full_annual_fee,
        statutory_due_date=statutory_due_date,
        payment_date=payment_date,
        rate=statutory_rate,
        late_fee_amount=_multiply_and_quantize_cents(full_annual_fee, statutory_rate),
        band_start_date=statutory_start,
        band_end_date=statutory_end,
        calculation_source=AnnuityLateFeeCalculationSource.STATUTORY,
        source_document_id=None,
    )
