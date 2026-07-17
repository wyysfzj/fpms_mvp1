from __future__ import annotations

import inspect
from dataclasses import MISSING, FrozenInstanceError, fields, is_dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from typing import get_type_hints

import pytest

import app.modules.fees.late_fee as late_fee
from app.modules.fees.late_fee import (
    AnnuityLateFeeCalculationSource,
    AnnuityLateFeeErrorCode,
    AnnuityLateFeeNotificationBand,
    AnnuityLateFeeResult,
    AnnuityLateFeeRuleError,
    CalculateAnnuityLateFeeCommand,
    calculate_annuity_late_fee,
)

EXPECTED_EXPORTS = (
    "AnnuityLateFeeCalculationSource",
    "AnnuityLateFeeErrorCode",
    "AnnuityLateFeeNotificationBand",
    "CalculateAnnuityLateFeeCommand",
    "AnnuityLateFeeResult",
    "AnnuityLateFeeRuleError",
    "calculate_annuity_late_fee",
)

EXPECTED_ENUM_VALUES = {
    AnnuityLateFeeCalculationSource: (
        ("STATUTORY", "STATUTORY"),
        ("NOTIFICATION", "NOTIFICATION"),
    ),
    AnnuityLateFeeErrorCode: (
        ("INVALID_FULL_ANNUAL_FEE", "INVALID_FULL_ANNUAL_FEE"),
        ("PAYMENT_BEFORE_DUE_DATE", "PAYMENT_BEFORE_DUE_DATE"),
        ("PAYMENT_AFTER_LATE_WINDOW", "PAYMENT_AFTER_LATE_WINDOW"),
        ("INVALID_NOTIFICATION_BAND", "INVALID_NOTIFICATION_BAND"),
        ("NOTIFICATION_BAND_OVERLAP", "NOTIFICATION_BAND_OVERLAP"),
        ("NOTIFICATION_BAND_GAP", "NOTIFICATION_BAND_GAP"),
    ),
}

EXPECTED_FIELDS = {
    AnnuityLateFeeNotificationBand: (
        ("start_date", date),
        ("end_date", date),
        ("rate", Decimal),
        ("amount", Decimal),
        ("source_document_id", str),
    ),
    CalculateAnnuityLateFeeCommand: (
        ("full_annual_fee", Decimal),
        ("statutory_due_date", date),
        ("payment_date", date),
        (
            "notification_bands",
            tuple[AnnuityLateFeeNotificationBand, ...],
        ),
    ),
    AnnuityLateFeeResult: (
        ("full_annual_fee", Decimal),
        ("statutory_due_date", date),
        ("payment_date", date),
        ("rate", Decimal),
        ("late_fee_amount", Decimal),
        ("band_start_date", date),
        ("band_end_date", date),
        ("calculation_source", AnnuityLateFeeCalculationSource),
        ("source_document_id", str | None),
    ),
}


def _band(
    start_date: date,
    end_date: date,
    rate: str,
    amount: str,
    source_document_id: str = "DOC-001",
) -> AnnuityLateFeeNotificationBand:
    return AnnuityLateFeeNotificationBand(
        start_date=start_date,
        end_date=end_date,
        rate=Decimal(rate),
        amount=Decimal(amount),
        source_document_id=source_document_id,
    )


def _calculate(
    *,
    full_annual_fee: Decimal = Decimal("1200"),
    due_date: date = date(2025, 1, 15),
    payment_date: date = date(2025, 1, 15),
    notification_bands: tuple[AnnuityLateFeeNotificationBand, ...] = (),
) -> AnnuityLateFeeResult:
    return calculate_annuity_late_fee(
        CalculateAnnuityLateFeeCommand(
            full_annual_fee=full_annual_fee,
            statutory_due_date=due_date,
            payment_date=payment_date,
            notification_bands=notification_bands,
        )
    )


def _assert_error(
    code: AnnuityLateFeeErrorCode,
    **overrides: object,
) -> AnnuityLateFeeRuleError:
    values: dict[str, object] = {
        "full_annual_fee": Decimal("1200"),
        "due_date": date(2025, 1, 15),
        "payment_date": date(2025, 1, 15),
        "notification_bands": (),
    }
    values.update(overrides)

    with pytest.raises(AnnuityLateFeeRuleError) as caught:
        _calculate(**values)  # type: ignore[arg-type]

    assert caught.value.code is code
    assert str(caught.value) == code.value
    return caught.value


def test_public_contract_is_exact_and_immutable() -> None:
    assert late_fee.__all__ == EXPECTED_EXPORTS

    for enum_type, expected_members in EXPECTED_ENUM_VALUES.items():
        assert issubclass(enum_type, str)
        assert issubclass(enum_type, Enum)
        assert tuple((member.name, member.value) for member in enum_type) == expected_members

    for dto_type, expected_fields in EXPECTED_FIELDS.items():
        assert is_dataclass(dto_type)
        assert dto_type.__dataclass_params__.frozen is True
        assert "__slots__" in dto_type.__dict__
        assert tuple(field.name for field in fields(dto_type)) == tuple(
            field_name for field_name, _annotation in expected_fields
        )
        assert get_type_hints(dto_type) == dict(expected_fields)

    command_fields = fields(CalculateAnnuityLateFeeCommand)
    assert all(field.default is MISSING for field in command_fields[:3])
    assert command_fields[3].default == ()
    assert command_fields[3].default_factory is MISSING
    assert all(
        field.default is MISSING and field.default_factory is MISSING
        for dto_type in (AnnuityLateFeeNotificationBand, AnnuityLateFeeResult)
        for field in fields(dto_type)
    )

    command = CalculateAnnuityLateFeeCommand(
        full_annual_fee=Decimal("1200"),
        statutory_due_date=date(2025, 1, 15),
        payment_date=date(2025, 2, 15),
    )
    band = _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60")
    result = AnnuityLateFeeResult(
        full_annual_fee=Decimal("1200"),
        statutory_due_date=date(2025, 1, 15),
        payment_date=date(2025, 2, 15),
        rate=Decimal("0.05"),
        late_fee_amount=Decimal("60.00"),
        band_start_date=date(2025, 2, 15),
        band_end_date=date(2025, 3, 14),
        calculation_source=AnnuityLateFeeCalculationSource.STATUTORY,
        source_document_id=None,
    )
    for instance, field_name, replacement in (
        (command, "payment_date", date(2025, 2, 16)),
        (band, "amount", Decimal("62")),
        (result, "payment_date", date(2025, 2, 16)),
    ):
        assert not hasattr(instance, "__dict__")
        with pytest.raises(FrozenInstanceError):
            setattr(instance, field_name, replacement)

    signature = inspect.signature(calculate_annuity_late_fee)
    assert tuple(signature.parameters) == ("command",)
    assert signature.parameters["command"].kind is inspect.Parameter.POSITIONAL_ONLY
    assert get_type_hints(calculate_annuity_late_fee) == {
        "command": CalculateAnnuityLateFeeCommand,
        "return": AnnuityLateFeeResult,
    }


def test_rule_error_code_is_read_only_and_message_is_exact() -> None:
    error = AnnuityLateFeeRuleError(AnnuityLateFeeErrorCode.PAYMENT_BEFORE_DUE_DATE)

    assert error.code is AnnuityLateFeeErrorCode.PAYMENT_BEFORE_DUE_DATE
    assert str(error) == "PAYMENT_BEFORE_DUE_DATE"
    with pytest.raises(AttributeError):
        error.code = AnnuityLateFeeErrorCode.INVALID_FULL_ANNUAL_FEE  # type: ignore[misc]


@pytest.mark.parametrize(
    ("payment_date", "expected_rate", "band_start", "band_end"),
    [
        (date(2025, 1, 15), "0", date(2025, 1, 15), date(2025, 2, 14)),
        (date(2025, 2, 14), "0", date(2025, 1, 15), date(2025, 2, 14)),
        (date(2025, 2, 15), "0.05", date(2025, 2, 15), date(2025, 3, 14)),
        (date(2025, 3, 15), "0.10", date(2025, 3, 15), date(2025, 4, 14)),
        (date(2025, 4, 15), "0.15", date(2025, 4, 15), date(2025, 5, 14)),
        (date(2025, 5, 15), "0.20", date(2025, 5, 15), date(2025, 6, 14)),
        (date(2025, 6, 15), "0.25", date(2025, 6, 15), date(2025, 7, 15)),
        (date(2025, 7, 15), "0.25", date(2025, 6, 15), date(2025, 7, 15)),
    ],
)
def test_statutory_anniversary_boundaries_are_inclusive(
    payment_date: date,
    expected_rate: str,
    band_start: date,
    band_end: date,
) -> None:
    result = _calculate(payment_date=payment_date)

    assert result == AnnuityLateFeeResult(
        full_annual_fee=Decimal("1200"),
        statutory_due_date=date(2025, 1, 15),
        payment_date=payment_date,
        rate=Decimal(expected_rate),
        late_fee_amount=(Decimal("1200") * Decimal(expected_rate)).quantize(Decimal("0.01")),
        band_start_date=band_start,
        band_end_date=band_end,
        calculation_source=AnnuityLateFeeCalculationSource.STATUTORY,
        source_document_id=None,
    )


def test_day_after_six_month_endpoint_fails_closed() -> None:
    _assert_error(
        AnnuityLateFeeErrorCode.PAYMENT_AFTER_LATE_WINDOW,
        payment_date=date(2025, 7, 16),
    )


def test_month_end_clamps_each_calendar_anniversary() -> None:
    zero_result = _calculate(
        due_date=date(2025, 1, 31),
        payment_date=date(2025, 2, 27),
    )
    five_percent_result = _calculate(
        due_date=date(2025, 1, 31),
        payment_date=date(2025, 2, 28),
    )

    assert (zero_result.band_start_date, zero_result.band_end_date) == (
        date(2025, 1, 31),
        date(2025, 2, 27),
    )
    assert zero_result.rate == Decimal("0")
    assert (five_percent_result.band_start_date, five_percent_result.band_end_date) == (
        date(2025, 2, 28),
        date(2025, 3, 30),
    )
    assert five_percent_result.rate == Decimal("0.05")


@pytest.mark.parametrize(
    ("due_date", "six_month_endpoint"),
    [
        (date(2024, 8, 31), date(2025, 2, 28)),
        (date(2023, 8, 31), date(2024, 2, 29)),
    ],
)
def test_six_month_endpoint_clamps_for_non_leap_and_leap_years(
    due_date: date,
    six_month_endpoint: date,
) -> None:
    result = _calculate(due_date=due_date, payment_date=six_month_endpoint)

    assert result.rate == Decimal("0.25")
    assert result.band_end_date == six_month_endpoint
    _assert_error(
        AnnuityLateFeeErrorCode.PAYMENT_AFTER_LATE_WINDOW,
        due_date=due_date,
        payment_date=six_month_endpoint + timedelta(days=1),
    )


def test_statutory_amount_uses_unreduced_full_fee_and_rounds_final_amount_half_up() -> None:
    ordinary = _calculate(payment_date=date(2025, 2, 15))
    rounding = _calculate(
        full_annual_fee=Decimal("100.10"),
        payment_date=date(2025, 2, 15),
    )

    assert ordinary.full_annual_fee == Decimal("1200")
    assert ordinary.rate == Decimal("0.05")
    assert ordinary.late_fee_amount == Decimal("60.00")
    assert rounding.full_annual_fee == Decimal("100.10")
    assert rounding.rate == Decimal("0.05")
    assert rounding.late_fee_amount == Decimal("5.01")


def test_matching_reviewed_notice_amount_overrides_statutory_calculation() -> None:
    notice = _band(
        date(2025, 2, 15),
        date(2025, 3, 14),
        "0.05",
        "61",
        "NOTICE-001",
    )

    result = _calculate(
        payment_date=date(2025, 2, 15),
        notification_bands=(notice,),
    )

    assert result == AnnuityLateFeeResult(
        full_annual_fee=Decimal("1200"),
        statutory_due_date=date(2025, 1, 15),
        payment_date=date(2025, 2, 15),
        rate=Decimal("0.05"),
        late_fee_amount=Decimal("61.00"),
        band_start_date=date(2025, 2, 15),
        band_end_date=date(2025, 3, 14),
        calculation_source=AnnuityLateFeeCalculationSource.NOTIFICATION,
        source_document_id="NOTICE-001",
    )


def test_notice_stated_amount_is_rounded_half_up_without_recalculation() -> None:
    notice = _band(
        date(2025, 2, 15),
        date(2025, 3, 14),
        "0.05",
        "61.005",
    )

    result = _calculate(
        payment_date=date(2025, 3, 14),
        notification_bands=(notice,),
    )

    assert result.late_fee_amount == Decimal("61.01")
    assert result.rate == Decimal("0.05")
    assert result.band_start_date == date(2025, 2, 15)
    assert result.band_end_date == date(2025, 3, 14)


def test_large_finite_statutory_amount_quantizes_without_context_leakage() -> None:
    result = _calculate(
        full_annual_fee=Decimal("1E+30"),
        payment_date=date(2025, 2, 15),
    )

    assert result.late_fee_amount == Decimal("50000000000000000000000000000.00")
    assert result.late_fee_amount.as_tuple().exponent == -2


def test_large_finite_notice_amount_quantizes_without_context_leakage() -> None:
    notice = _band(
        date(2025, 2, 15),
        date(2025, 3, 14),
        "0.05",
        "1E+30",
    )

    result = _calculate(
        payment_date=date(2025, 2, 15),
        notification_bands=(notice,),
    )

    assert result.late_fee_amount == Decimal("1000000000000000000000000000000.00")
    assert result.late_fee_amount.as_tuple().exponent == -2


def test_real_sample_notice_shape_is_sorted_and_leading_zero_period_falls_back() -> None:
    bands = (
        _band(date(2026, 3, 13), date(2026, 4, 13), "0.25", "300", "DOC-25"),
        _band(date(2026, 2, 13), date(2026, 3, 12), "0.20", "240", "DOC-20"),
        _band(date(2026, 1, 13), date(2026, 2, 12), "0.15", "180", "DOC-15"),
        _band(date(2025, 12, 13), date(2026, 1, 12), "0.10", "120", "DOC-10"),
        _band(date(2025, 11, 13), date(2025, 12, 12), "0.05", "60", "DOC-05"),
    )

    leading_zero_result = _calculate(
        due_date=date(2025, 10, 13),
        payment_date=date(2025, 11, 12),
        notification_bands=bands,
    )
    final_notice_result = _calculate(
        due_date=date(2025, 10, 13),
        payment_date=date(2026, 4, 13),
        notification_bands=bands,
    )

    assert leading_zero_result.calculation_source is AnnuityLateFeeCalculationSource.STATUTORY
    assert leading_zero_result.rate == Decimal("0")
    assert leading_zero_result.late_fee_amount == Decimal("0.00")
    assert leading_zero_result.source_document_id is None
    assert final_notice_result.calculation_source is AnnuityLateFeeCalculationSource.NOTIFICATION
    assert final_notice_result.source_document_id == "DOC-25"
    assert final_notice_result.rate == Decimal("0.25")
    assert final_notice_result.late_fee_amount == Decimal("300.00")


@pytest.mark.parametrize(
    "full_annual_fee",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_invalid_full_annual_fee_forms_fail_closed(full_annual_fee: Decimal) -> None:
    _assert_error(
        AnnuityLateFeeErrorCode.INVALID_FULL_ANNUAL_FEE,
        full_annual_fee=full_annual_fee,
    )


def test_payment_before_due_date_fails_closed() -> None:
    _assert_error(
        AnnuityLateFeeErrorCode.PAYMENT_BEFORE_DUE_DATE,
        payment_date=date(2025, 1, 14),
    )


@pytest.mark.parametrize(
    "invalid_band",
    [
        _band(date(2025, 3, 15), date(2025, 3, 14), "0.10", "120"),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.30", "60"),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "-1"),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "NaN"),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "Infinity"),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60", ""),
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60", "   "),
        _band(date(2025, 1, 14), date(2025, 2, 14), "0", "0"),
        _band(date(2025, 7, 15), date(2025, 7, 16), "0.25", "300"),
    ],
)
def test_invalid_notice_band_forms_fail_closed(
    invalid_band: AnnuityLateFeeNotificationBand,
) -> None:
    _assert_error(
        AnnuityLateFeeErrorCode.INVALID_NOTIFICATION_BAND,
        notification_bands=(invalid_band,),
    )


@pytest.mark.parametrize(
    "invalid_rate",
    [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity")],
)
def test_non_finite_notice_rates_raise_domain_error_without_decimal_leakage(
    invalid_rate: Decimal,
) -> None:
    invalid_band = AnnuityLateFeeNotificationBand(
        start_date=date(2025, 2, 15),
        end_date=date(2025, 3, 14),
        rate=invalid_rate,
        amount=Decimal("60"),
        source_document_id="DOC-001",
    )

    _assert_error(
        AnnuityLateFeeErrorCode.INVALID_NOTIFICATION_BAND,
        notification_bands=(invalid_band,),
    )


def test_overlapping_notification_bands_fail_closed() -> None:
    bands = (
        _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60", "A"),
        _band(date(2025, 3, 14), date(2025, 4, 14), "0.10", "120", "B"),
    )

    _assert_error(
        AnnuityLateFeeErrorCode.NOTIFICATION_BAND_OVERLAP,
        payment_date=date(2025, 3, 14),
        notification_bands=bands,
    )


def test_internal_notification_band_gap_fails_closed() -> None:
    bands = (
        _band(date(2025, 2, 15), date(2025, 3, 13), "0.05", "60", "A"),
        _band(date(2025, 3, 15), date(2025, 4, 14), "0.10", "120", "B"),
    )

    _assert_error(
        AnnuityLateFeeErrorCode.NOTIFICATION_BAND_GAP,
        payment_date=date(2025, 3, 14),
        notification_bands=bands,
    )


def test_uncovered_non_zero_payment_date_fails_closed() -> None:
    later_band = _band(
        date(2025, 3, 15),
        date(2025, 4, 14),
        "0.10",
        "120",
    )

    _assert_error(
        AnnuityLateFeeErrorCode.NOTIFICATION_BAND_GAP,
        payment_date=date(2025, 2, 15),
        notification_bands=(later_band,),
    )


@pytest.mark.parametrize(
    ("expected_code", "overrides"),
    [
        (
            AnnuityLateFeeErrorCode.INVALID_FULL_ANNUAL_FEE,
            {
                "full_annual_fee": Decimal("NaN"),
                "payment_date": date(2025, 1, 14),
                "notification_bands": (_band(date(2025, 3, 15), date(2025, 3, 14), "0.10", "120"),),
            },
        ),
        (
            AnnuityLateFeeErrorCode.PAYMENT_BEFORE_DUE_DATE,
            {
                "payment_date": date(2025, 1, 14),
                "notification_bands": (_band(date(2025, 3, 15), date(2025, 3, 14), "0.10", "120"),),
            },
        ),
        (
            AnnuityLateFeeErrorCode.PAYMENT_AFTER_LATE_WINDOW,
            {
                "payment_date": date(2025, 7, 16),
                "notification_bands": (_band(date(2025, 3, 15), date(2025, 3, 14), "0.10", "120"),),
            },
        ),
        (
            AnnuityLateFeeErrorCode.INVALID_NOTIFICATION_BAND,
            {
                "payment_date": date(2025, 3, 14),
                "notification_bands": (
                    _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60", "A"),
                    _band(date(2025, 3, 14), date(2025, 4, 14), "0.30", "120", "B"),
                ),
            },
        ),
        (
            AnnuityLateFeeErrorCode.NOTIFICATION_BAND_OVERLAP,
            {
                "payment_date": date(2025, 3, 14),
                "notification_bands": (
                    _band(date(2025, 2, 15), date(2025, 3, 14), "0.05", "60", "A"),
                    _band(date(2025, 3, 14), date(2025, 4, 13), "0.10", "120", "B"),
                    _band(date(2025, 4, 15), date(2025, 5, 14), "0.15", "180", "C"),
                ),
            },
        ),
    ],
)
def test_multiple_invalid_conditions_follow_exact_error_order(
    expected_code: AnnuityLateFeeErrorCode,
    overrides: dict[str, object],
) -> None:
    _assert_error(expected_code, **overrides)
