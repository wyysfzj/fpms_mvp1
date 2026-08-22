from datetime import date
from decimal import Decimal
from unittest import TestCase

from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList


class _Scalars:
    def __init__(self, values: list[object]) -> None:
        self._values = values

    def all(self) -> list[object]:
        return self._values


class _Result:
    def __init__(self, values: list[object]) -> None:
        self._values = values

    def scalar_one_or_none(self) -> object | None:
        return self._values[0] if self._values else None

    def scalars(self) -> _Scalars:
        return _Scalars(self._values)


class _Transaction:
    def __init__(self, pay_list: PayList, payments: list[GovPayment]) -> None:
        self.pay_list = pay_list
        self.payments = payments
        self.commits = 0
        self.refreshed: list[object] = []

    def execute(self, statement: object) -> _Result:
        sql = str(statement)
        if "t_gov_payment" in sql:
            return _Result(self.payments)
        if "t_pay_list" in sql:
            return _Result([self.pay_list])
        raise AssertionError(f"unexpected query: {sql}")

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, instance: object) -> None:
        self.refreshed.append(instance)


class MarkPayListPaidDecoupleTests(TestCase):
    def test_mark_paid_relies_on_payment_evidence_without_export_status(self) -> None:
        pay_list = PayList(
            id=7,
            client_id="client-1",
            pay_list_no="PL-000007",
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("100.00"),
        )
        payment = GovPayment(
            id=11,
            pay_list_id=pay_list.id,
            case_id="case-1",
            status="PAID",
            currency="CNY",
            paid_date=date(2026, 7, 20),
            paid_amount=Decimal("100.00"),
        )
        transaction = _Transaction(pay_list, [payment])

        result = service.mark_pay_list_paid(
            transaction,
            pay_list_id=pay_list.id,
            paid_date=date(2026, 7, 21),
            actor_id="actor-1",
        )

        self.assertEqual(result["pay_list"]["status"], "PAID")
        self.assertEqual(result["pay_list"]["paid_date"], date(2026, 7, 21))
        self.assertEqual(pay_list.status, "PAID")
        self.assertEqual(pay_list.paid_date, date(2026, 7, 21))
        self.assertEqual(pay_list.updated_by, "actor-1")
        self.assertEqual(transaction.commits, 1)
        self.assertEqual(transaction.refreshed, [pay_list])
