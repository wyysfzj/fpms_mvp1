from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime
from decimal import Decimal
from inspect import signature

from app.core.errors import BusinessError
from app.modules.fees import official_rate_book


class PatentTermCompensationRequestFeeRuleTests(unittest.TestCase):
    def _public_boundary(self):
        expected = (
            "GetPatentTermCompensationRequestFeeCommand",
            "GetPatentTermCompensationRequestFeeResult",
            "get_patent_term_compensation_request_fee",
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

    def test_exposes_exact_immutable_pure_public_boundary(self) -> None:
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
        self.assertEqual(tuple(signature(rule).parameters), ("command",))

        command = command_type(effective_date=date(2024, 8, 6))
        result = rule(command)
        for instance, field_name, value in (
            (command, "effective_date", date(2024, 8, 7)),
            (result, "amount", Decimal("999.00")),
        ):
            self.assertFalse(hasattr(instance, "__dict__"))
            with self.assertRaises(FrozenInstanceError):
                setattr(instance, field_name, value)

    def test_returns_exact_source_bound_fee_on_and_after_effective_date(self) -> None:
        _, _, rule = self._public_boundary()

        for effective_date in (date(2024, 8, 6), date(2035, 12, 31)):
            with self.subTest(effective_date=effective_date):
                result = rule(self._command(effective_date))

                self.assertEqual(
                    result.fee_code,
                    "CN_PATENT_TERM_COMPENSATION_REQUEST_FEE",
                )
                self.assertEqual(result.currency, "CNY")
                self.assertEqual(result.amount, Decimal("200.00"))
                self.assertEqual(result.effective_from, date(2024, 8, 6))
                self.assertEqual(
                    result.source_reference,
                    "CNIPA_ANNOUNCEMENT_594_AND_PAYMENT_GUIDE_20260330",
                )
                self.assertEqual(result.source_version, "2024-08-06/2026-03-30")
                self.assertEqual(
                    result.source_snapshot_hash,
                    "e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544",
                )

    def test_rejects_invalid_command_or_effective_date(self) -> None:
        _, _, rule = self._public_boundary()

        invalid_commands = (
            object(),
            None,
            self._command(None),
            self._command("2024-08-06"),
            self._command(datetime(2024, 8, 6)),
        )
        for command in invalid_commands:
            with self.subTest(command=command):
                with self.assertRaises(BusinessError) as caught:
                    rule(command)
                self.assertEqual(caught.exception.status_code, 400)
                self.assertEqual(
                    caught.exception.code,
                    "PATENT_TERM_COMPENSATION_REQUEST_FEE_INVALID_INPUT",
                )
                self.assertEqual(
                    caught.exception.details,
                    {"field": "effective_date"},
                )

    def test_rejects_pre_effective_date_with_exact_requested_date_details(self) -> None:
        _, _, rule = self._public_boundary()

        for requested_date in (date(2024, 8, 5), date(2000, 1, 1)):
            with self.subTest(requested_date=requested_date):
                with self.assertRaises(BusinessError) as caught:
                    rule(self._command(requested_date))

                self.assertEqual(caught.exception.status_code, 400)
                self.assertEqual(
                    caught.exception.code,
                    "PATENT_TERM_COMPENSATION_REQUEST_FEE_UNAVAILABLE",
                )
                self.assertEqual(
                    caught.exception.details,
                    {
                        "effective_date": requested_date.isoformat(),
                        "effective_from": "2024-08-06",
                    },
                )


if __name__ == "__main__":
    unittest.main()
