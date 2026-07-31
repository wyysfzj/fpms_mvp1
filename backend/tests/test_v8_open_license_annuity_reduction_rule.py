from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, fields
from decimal import Decimal
from inspect import signature

from app.core.errors import BusinessError
from app.modules.fees import official_rate_book


class OpenLicenseAnnuityReductionRuleTests(unittest.TestCase):
    def _public_boundary(self):
        expected = (
            "CalculateOpenLicenseAnnuityReductionCommand",
            "CalculateOpenLicenseAnnuityReductionResult",
            "calculate_open_license_annuity_reduction",
        )
        missing = tuple(
            name
            for name in expected
            if name not in official_rate_book.__all__ or not hasattr(official_rate_book, name)
        )
        self.assertEqual(missing, ())
        return tuple(getattr(official_rate_book, name) for name in expected)

    def _command(self, existing_reduction_ratio: object):
        command_type, _, _ = self._public_boundary()
        return command_type(existing_reduction_ratio=existing_reduction_ratio)

    def _assert_error(
        self,
        command: object,
        *,
        details: dict[str, str],
    ) -> None:
        _, _, rule = self._public_boundary()
        with self.assertRaises(BusinessError) as caught:
            rule(command)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertEqual(
            caught.exception.code,
            "OPEN_LICENSE_ANNUITY_REDUCTION_INVALID_INPUT",
        )
        self.assertEqual(caught.exception.details, details)

    def test_exposes_exact_immutable_pure_public_boundary(self) -> None:
        command_type, result_type, rule = self._public_boundary()

        self.assertEqual(
            tuple(field.name for field in fields(command_type)),
            ("existing_reduction_ratio",),
        )
        self.assertEqual(
            tuple(field.name for field in fields(result_type)),
            (
                "open_license_reduction_ratio",
                "existing_reduction_ratio",
                "applied_reduction_ratio",
                "payable_ratio",
            ),
        )
        self.assertEqual(tuple(signature(rule).parameters), ("command",))

        command = command_type(existing_reduction_ratio=Decimal("0"))
        result = rule(command)
        for instance, field_name, value in (
            (command, "existing_reduction_ratio", Decimal("0.70")),
            (result, "applied_reduction_ratio", Decimal("0.85")),
        ):
            self.assertFalse(hasattr(instance, "__dict__"))
            with self.assertRaises(FrozenInstanceError):
                setattr(instance, field_name, value)

    def test_applies_fifteen_percent_when_it_is_the_best_benefit(self) -> None:
        _, result_type, rule = self._public_boundary()

        self.assertEqual(
            rule(self._command(Decimal("0"))),
            result_type(
                open_license_reduction_ratio=Decimal("0.15"),
                existing_reduction_ratio=Decimal("0"),
                applied_reduction_ratio=Decimal("0.15"),
                payable_ratio=Decimal("0.85"),
            ),
        )

    def test_keeps_a_better_existing_benefit_without_stacking(self) -> None:
        _, result_type, rule = self._public_boundary()

        for existing_reduction_ratio, expected_payable_ratio in (
            (Decimal("0.70"), Decimal("0.30")),
            (Decimal("0.85"), Decimal("0.15")),
        ):
            with self.subTest(existing_reduction_ratio=existing_reduction_ratio):
                self.assertEqual(
                    rule(self._command(existing_reduction_ratio)),
                    result_type(
                        open_license_reduction_ratio=Decimal("0.15"),
                        existing_reduction_ratio=existing_reduction_ratio,
                        applied_reduction_ratio=existing_reduction_ratio,
                        payable_ratio=expected_payable_ratio,
                    ),
                )

    def test_rejects_wrong_command_type(self) -> None:
        for command in (object(), None):
            with self.subTest(command=command):
                self._assert_error(command, details={"field": "command"})

    def test_rejects_non_decimal_non_finite_or_unsupported_existing_ratio(self) -> None:
        for existing_reduction_ratio in (
            0,
            0.7,
            "0.70",
            None,
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("0.10"),
            Decimal("0.15"),
            Decimal("0.71"),
            Decimal("1"),
            Decimal("-0.01"),
            Decimal("1.01"),
        ):
            with self.subTest(existing_reduction_ratio=existing_reduction_ratio):
                self._assert_error(
                    self._command(existing_reduction_ratio),
                    details={"field": "existing_reduction_ratio"},
                )


if __name__ == "__main__":
    unittest.main()
