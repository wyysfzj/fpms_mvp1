from __future__ import annotations

from decimal import Decimal, localcontext

import pytest

from app.modules.fees import obligation_service


@pytest.mark.parametrize(
    ("eligible_ratio", "expected_payable"),
    [
        ("1.0000", "1200.00"),
        ("0.3000", "360.00"),
        ("0.1500", "180.00"),
    ],
)
def test_yearly_payable_amount_uses_eligible_ratio_and_keeps_full_late_fee_base(
    eligible_ratio: str,
    expected_payable: str,
) -> None:
    result = obligation_service.calculate_annuity_payable_amount(
        full_annual_fee=Decimal("1200.00"),
        eligible_ratio=Decimal(eligible_ratio),
    )

    assert result == obligation_service.AnnuityPayableAmountResult(
        full_annual_fee=Decimal("1200.00"),
        eligible_ratio=Decimal(eligible_ratio),
        payable_amount=Decimal(expected_payable),
        late_fee_base=Decimal("1200.00"),
    )


def test_payable_amount_rounds_only_the_final_product_half_up() -> None:
    result = obligation_service.calculate_annuity_payable_amount(
        full_annual_fee=Decimal("100.10"),
        eligible_ratio=Decimal("0.05"),
    )

    assert result.payable_amount == Decimal("5.01")
    assert result.late_fee_base == Decimal("100.10")


def test_valid_inputs_do_not_inherit_small_caller_decimal_precision() -> None:
    with localcontext() as context:
        context.prec = 2
        result = obligation_service.calculate_annuity_payable_amount(
            full_annual_fee=Decimal("1200.00"),
            eligible_ratio=Decimal("0.3000"),
        )

    assert result.payable_amount == Decimal("360.00")
    assert result.late_fee_base == Decimal("1200.00")


def test_exact_maximum_full_annual_fee_is_accepted() -> None:
    maximum = Decimal("9999999999999999.99")

    result = obligation_service.calculate_annuity_payable_amount(
        full_annual_fee=maximum,
        eligible_ratio=Decimal("1"),
    )

    assert result.payable_amount == maximum
    assert result.late_fee_base == maximum


def test_first_cent_above_maximum_full_annual_fee_fails_closed() -> None:
    with pytest.raises(ValueError, match="^ANNUITY_FULL_ANNUAL_FEE_INVALID$"):
        obligation_service.calculate_annuity_payable_amount(
            full_annual_fee=Decimal("10000000000000000.00"),
            eligible_ratio=Decimal("1"),
        )


@pytest.mark.parametrize(
    "full_annual_fee",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("Infinity"),
        1200,
    ],
)
def test_invalid_full_annual_fee_fails_closed(full_annual_fee: object) -> None:
    with pytest.raises(ValueError, match="^ANNUITY_FULL_ANNUAL_FEE_INVALID$"):
        obligation_service.calculate_annuity_payable_amount(
            full_annual_fee=full_annual_fee,  # type: ignore[arg-type]
            eligible_ratio=Decimal("0.30"),
        )


@pytest.mark.parametrize(
    "eligible_ratio",
    [
        Decimal("0"),
        Decimal("-0.01"),
        Decimal("1.01"),
        Decimal("NaN"),
        Decimal("Infinity"),
        0.3,
    ],
)
def test_invalid_eligible_ratio_fails_closed(eligible_ratio: object) -> None:
    with pytest.raises(ValueError, match="^ANNUITY_ELIGIBLE_RATIO_INVALID$"):
        obligation_service.calculate_annuity_payable_amount(
            full_annual_fee=Decimal("1200.00"),
            eligible_ratio=eligible_ratio,  # type: ignore[arg-type]
        )
