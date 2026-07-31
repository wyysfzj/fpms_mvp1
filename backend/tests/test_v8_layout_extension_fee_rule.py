from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime
from decimal import Decimal

from app.core.errors import BusinessError
from app.modules.fees import official_rate_book


class LayoutExtensionFeeRuleTests(unittest.TestCase):
    def _public_boundary(self):
        expected = (
            "GetLayoutExtensionFeeCommand",
            "GetLayoutExtensionFeeResult",
            "get_layout_extension_fee",
        )
        missing = tuple(
            name
            for name in expected
            if name not in official_rate_book.__all__ or not hasattr(official_rate_book, name)
        )
        self.assertEqual(missing, ())
        return tuple(getattr(official_rate_book, name) for name in expected)

    def _command(self, effective_date: object):
        command_type, _, _ = self._public_boundary()
        return command_type(effective_date=effective_date)

    def test_exposes_exact_immutable_public_boundary(self) -> None:
        command_type, result_type, rule = self._public_boundary()

        self.assertEqual(
            tuple(field.name for field in fields(command_type)),
            ("effective_date",),
        )
        self.assertEqual(
            tuple(field.name for field in fields(result_type)),
            (
                "fee_code",
                "currency",
                "amount",
                "effective_from",
                "source_reference",
                "source_version",
                "source_snapshot_hash",
            ),
        )

        command = command_type(effective_date=date(2017, 7, 1))
        result = rule(command)
        for instance, field_name, value in (
            (command, "effective_date", date(2017, 7, 2)),
            (result, "amount", Decimal("999.00")),
        ):
            self.assertFalse(hasattr(instance, "__dict__"))
            with self.assertRaises(FrozenInstanceError):
                setattr(instance, field_name, value)

    def test_returns_exact_source_bound_fee_on_and_after_effective_date(self) -> None:
        _, _, rule = self._public_boundary()

        for effective_date in (date(2017, 7, 1), date(2035, 12, 31)):
            with self.subTest(effective_date=effective_date):
                result = rule(self._command(effective_date))

                self.assertEqual(
                    result.fee_code,
                    "IC_LAYOUT_EXTENSION_REQUEST_FEE",
                )
                self.assertEqual(result.currency, "CNY")
                self.assertEqual(result.amount, Decimal("150.00"))
                self.assertEqual(result.effective_from, date(2017, 7, 1))
                self.assertEqual(
                    result.source_reference,
                    "https://www.cnipa.gov.cn/art/2017/6/30/art_74_27462.html",
                )
                self.assertEqual(result.source_version, "2017-07-01")
                self.assertEqual(
                    result.source_snapshot_hash,
                    "f05e0f4200ce89a7cb1a8b5fb5d81508f76040a9a008b55969049460298cbfc4",
                )

    def test_rejects_wrong_command_or_unsupported_effective_date(self) -> None:
        _, _, rule = self._public_boundary()

        invalid_commands = (
            object(),
            None,
            self._command(None),
            self._command("2017-07-01"),
            self._command(datetime(2017, 7, 1)),
            self._command(date(2017, 6, 30)),
        )
        for command in invalid_commands:
            with self.subTest(command=command):
                with self.assertRaises(BusinessError) as caught:
                    rule(command)
                self.assertEqual(caught.exception.status_code, 400)
                self.assertEqual(
                    caught.exception.details,
                    {
                        "field": (
                            "command"
                            if type(command) is not official_rate_book.GetLayoutExtensionFeeCommand
                            else "effective_date"
                        )
                    },
                )


if __name__ == "__main__":
    unittest.main()
