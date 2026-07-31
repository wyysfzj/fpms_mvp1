from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime
from decimal import Decimal
from inspect import signature

from app.core.errors import BusinessError
from app.modules.fees import official_rate_book


class CompensationPeriodAnnuityFeeRuleTests(unittest.TestCase):
    def _public_boundary(self):
        expected = (
            "CalculateCompensationPeriodAnnuityFeeCommand",
            "CalculateCompensationPeriodAnnuityFeeResult",
            "calculate_compensation_period_annuity_fee",
        )
        missing = tuple(
            name
            for name in expected
            if name not in official_rate_book.__all__ or not hasattr(official_rate_book, name)
        )
        self.assertEqual(missing, ())
        return tuple(getattr(official_rate_book, name) for name in expected)

    def _command(self, effective_date: object, complete_years: object):
        command_type, _, _ = self._public_boundary()
        return command_type(
            effective_date=effective_date,
            complete_years=complete_years,
        )

    def _assert_error(
        self,
        command: object,
        *,
        code: str,
        details: dict[str, str],
    ) -> None:
        _, _, rule = self._public_boundary()
        with self.assertRaises(BusinessError) as caught:
            rule(command)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(caught.exception.details, details)

    def test_exposes_exact_immutable_pure_public_boundary(self) -> None:
        command_type, result_type, rule = self._public_boundary()

        self.assertEqual(
            tuple(field.name for field in fields(command_type)),
            ("effective_date", "complete_years"),
        )
        self.assertEqual(
            tuple(field.name for field in fields(result_type)),
            (
                "fee_code",
                "currency",
                "complete_years",
                "unit_amount",
                "amount",
                "effective_from",
                "source_reference",
                "source_version",
                "source_snapshot_hash",
            ),
        )
        self.assertEqual(tuple(signature(rule).parameters), ("command",))

        command = command_type(effective_date=date(2024, 7, 26), complete_years=1)
        result = rule(command)
        for instance, field_name, value in (
            (command, "complete_years", 2),
            (result, "amount", Decimal("999.00")),
        ):
            self.assertFalse(hasattr(instance, "__dict__"))
            with self.assertRaises(FrozenInstanceError):
                setattr(instance, field_name, value)

    def test_calculates_only_complete_years_on_and_after_effective_date(self) -> None:
        _, _, rule = self._public_boundary()

        for effective_date, complete_years, expected_amount in (
            (date(2024, 7, 26), 0, Decimal("0.00")),
            (date(2024, 7, 26), 1, Decimal("8000.00")),
            (date(2035, 12, 31), 3, Decimal("24000.00")),
        ):
            with self.subTest(
                effective_date=effective_date,
                complete_years=complete_years,
            ):
                result = rule(self._command(effective_date, complete_years))

                self.assertEqual(
                    result.fee_code,
                    "CN_COMPENSATION_PERIOD_ANNUITY_FEE",
                )
                self.assertEqual(result.currency, "CNY")
                self.assertEqual(result.complete_years, complete_years)
                self.assertEqual(result.unit_amount, Decimal("8000.00"))
                self.assertEqual(result.amount, expected_amount)
                self.assertEqual(result.effective_from, date(2024, 7, 26))
                self.assertEqual(
                    result.source_reference,
                    "NDRC_2024_1156_CNIPA_594_PAYMENT_NOTICE_AND_GUIDE_20260330",
                )
                self.assertEqual(
                    result.source_version,
                    "2024-07-26/2024-08-06/2026-03-30",
                )
                self.assertEqual(
                    result.source_snapshot_hash,
                    "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544",
                )

    def test_rejects_wrong_command_type(self) -> None:
        for command in (object(), None):
            with self.subTest(command=command):
                self._assert_error(
                    command,
                    code="COMPENSATION_PERIOD_ANNUITY_FEE_INVALID_INPUT",
                    details={"field": "command"},
                )

    def test_rejects_non_exact_effective_date(self) -> None:
        for effective_date in (None, "2024-07-26", datetime(2024, 7, 26)):
            with self.subTest(effective_date=effective_date):
                self._assert_error(
                    self._command(effective_date, 1),
                    code="COMPENSATION_PERIOD_ANNUITY_FEE_INVALID_INPUT",
                    details={"field": "effective_date"},
                )

    def test_rejects_non_exact_or_negative_complete_years(self) -> None:
        for complete_years in (
            True,
            1.0,
            Decimal("1"),
            "1",
            None,
            -1,
        ):
            with self.subTest(complete_years=complete_years):
                self._assert_error(
                    self._command(date(2024, 7, 26), complete_years),
                    code="COMPENSATION_PERIOD_ANNUITY_FEE_INVALID_INPUT",
                    details={"field": "complete_years"},
                )

    def test_rejects_pre_effective_date_with_exact_details(self) -> None:
        for requested_date in (date(2024, 7, 25), date(2000, 1, 1)):
            with self.subTest(requested_date=requested_date):
                self._assert_error(
                    self._command(requested_date, 1),
                    code="COMPENSATION_PERIOD_ANNUITY_FEE_UNAVAILABLE",
                    details={
                        "effective_date": requested_date.isoformat(),
                        "effective_from": "2024-07-26",
                    },
                )


if __name__ == "__main__":
    unittest.main()
