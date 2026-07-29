from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.models import Case
from app.modules.fees.models import FeeObligation
from app.modules.fees.obligation_contracts import (
    FeeClientInstructionStatus,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeOfficialEvidenceStatus,
    FeePaymentStatus,
)


class _Scalars:
    def __init__(self, *, first: Any = None, all_rows: list[Any] | None = None) -> None:
        self._first = first
        self._all_rows = all_rows or []

    def first(self) -> Any:
        return self._first

    def all(self) -> list[Any]:
        return self._all_rows


class _Result:
    def __init__(
        self,
        *,
        scalar: Any = None,
        first: Any = None,
        all_rows: list[Any] | None = None,
    ) -> None:
        self._scalar = scalar
        self._scalars = _Scalars(first=first, all_rows=all_rows)

    def scalar_one_or_none(self) -> Any:
        return self._scalar

    def scalars(self) -> _Scalars:
        return self._scalars


class _Transaction:
    def __init__(
        self,
        *,
        pay_list: PayList,
        payment: GovPayment,
        case: Case,
    ) -> None:
        self._results = iter(
            (
                _Result(scalar=pay_list),
                _Result(first=payment),
                _Result(first=None),
                _Result(all_rows=[payment]),
            )
        )
        self._case = case
        self.commits = 0

    def execute(self, _statement: Any) -> _Result:
        return next(self._results)

    def get(self, model: type[Any], object_id: Any) -> Any:
        assert model is Case
        assert object_id == self._case.id
        return self._case

    def flush(self) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, _instance: Any) -> None:
        return None


class OfficialPaymentEvidenceActivityAdapterTest(TestCase):
    def test_verified_receipt_changes_only_official_evidence_and_appends_own_activity(
        self,
    ) -> None:
        actor_id = "actor-official-evidence"
        case = Case(
            id="case-official-evidence",
            case_no="NO-OFFICIAL-EVIDENCE",
            client_id="client-official-evidence",
            status="OPEN",
            lifecycle_revision=1,
        )
        pay_list = PayList(
            id=41,
            client_id=case.client_id,
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("500.00"),
            created_by=actor_id,
            updated_by=actor_id,
        )
        payment = GovPayment(
            id=73,
            pay_list_id=pay_list.id,
            case_id=case.id,
            fee_item_id="fee-item-official-evidence",
            status="PLANNED",
            currency="CNY",
            paid_amount=Decimal("500.00"),
            planned_amt=Decimal("500.00"),
            planned_currency="CNY",
            created_by=actor_id,
            updated_by=actor_id,
        )
        obligation = FeeObligation(
            id="obligation-official-evidence",
            case_id=case.id,
            source_activity_id="activity-obligation-source",
            fee_domain="GOV",
            obligation_type="PATENT_APPLICATION",
            obligation_status=FeeObligationStatus.RECOGNIZED.value,
            due_date=date(2026, 8, 20),
            currency="CNY",
            source_status="VERIFIED",
            client_instruction_status=FeeClientInstructionStatus.PAY.value,
            draft_status=FeeObligationDraftStatus.CREATED.value,
            payment_status=FeePaymentStatus.UNPAID.value,
            official_evidence_status=FeeOfficialEvidenceStatus.PENDING.value,
            created_by=actor_id,
            updated_by=actor_id,
        )
        transaction = _Transaction(pay_list=pay_list, payment=payment, case=case)
        payment_activity_calls: list[int] = []
        official_activity_commands: list[Any] = []

        def record_payment_activity(*_args: Any, **kwargs: Any) -> None:
            payment_activity_calls.append(kwargs["payment"].id)
            obligation.payment_status = FeePaymentStatus.PAID.value

        with (
            patch.object(
                service,
                "_gov_payment_obligation_context",
                return_value=(obligation, ("line-official-evidence",)),
            ),
            patch.object(
                service,
                "_record_gov_payment_activity",
                side_effect=record_payment_activity,
            ),
            patch.object(
                service,
                "append_case_activity",
                side_effect=lambda command, *_args, **_kwargs: (
                    official_activity_commands.append(command)
                ),
            ),
        ):
            result = service.register_gov_payment(
                transaction,
                pay_list_id=pay_list.id,
                fee_item_id=payment.fee_item_id,
                paid_date=date(2026, 7, 20),
                official_receipt_no="CNIPA-RECEIPT-73",
                voucher_no="VOUCHER-73",
                invoice_no="INVOICE-73",
                actor_id=actor_id,
            )

        self.assertEqual(result["gov_payment"]["status"], "PAID")
        self.assertEqual(payment_activity_calls, [payment.id])
        self.assertEqual(obligation.payment_status, FeePaymentStatus.PAID.value)
        self.assertEqual(
            obligation.official_evidence_status,
            FeeOfficialEvidenceStatus.VERIFIED.value,
        )
        self.assertEqual(len(official_activity_commands), 1)
        command = official_activity_commands[0]
        self.assertEqual(command.event_type, "OFFICIAL_PAYMENT_EVIDENCE_VERIFIED")
        self.assertEqual(
            command.idempotency_key,
            f"gov-payment:{payment.id}:official-evidence-verified",
        )
        self.assertEqual(command.source_activity_id, obligation.source_activity_id)
        self.assertEqual(
            command.payload,
            {
                "gov_payment_id": payment.id,
                "invoice_no": "INVOICE-73",
                "obligation_id": obligation.id,
                "obligation_line_ids": ["line-official-evidence"],
                "official_receipt_no": "CNIPA-RECEIPT-73",
                "schema": "FPMS_GOV_PAYMENT_OFFICIAL_EVIDENCE_VERIFIED_V1",
                "voucher_no": "VOUCHER-73",
            },
        )
        self.assertEqual(transaction.commits, 1)
