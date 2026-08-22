from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy.sql import Select

from app.core.errors import BusinessError
from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact

PAY_LIST_FIELDS = (
    "id",
    "pay_list_no",
    "client_id",
    "status",
    "currency",
    "planned_pay_date",
    "paid_date",
    "total_amount",
    "remark",
    "list_type",
    "flow_dir",
    "invoice_no_from",
    "invoice_no_to",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)
GOV_PAYMENT_FIELDS = (
    "id",
    "pay_list_id",
    "case_id",
    "case_no",
    "fee_item_id",
    "status",
    "currency",
    "paid_date",
    "paid_amount",
    "official_receipt_no",
    "remark",
    "fee_code",
    "year_no",
    "planned_amt",
    "planned_currency",
    "paid_currency",
    "voucher_no",
    "invoice_no",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
)
EXPORT_ARTIFACT_FIELDS = (
    "id",
    "pay_list_id",
    "kind",
    "status",
    "content_sha256",
    "managed_storage_path",
    "template_version",
    "generated_by",
    "generated_at",
    "idempotency_key",
    "official_acceptance_evidence_ref",
    "official_acceptance_evidence_hash",
    "official_accepted_at",
    "updated_at",
)
OFFICIAL_WORKBOOK_FIELDS = (
    "official_upload_template_status",
    "official_upload_template_name",
    "official_upload_batch_limit",
    "official_pay_list_boundary_note",
)


class _Scalars:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


class _Result:
    def __init__(self, values: list[object]) -> None:
        self.values = values

    def scalar_one_or_none(self) -> object | None:
        return self.values[0] if self.values else None

    def scalars(self) -> _Scalars:
        return _Scalars(self.values)

    def all(self) -> list[object]:
        return self.values


class _NoAutoflush(AbstractContextManager[None]):
    def __init__(self, session: _ReadSession) -> None:
        self.session = session

    def __enter__(self) -> None:
        self.session.no_autoflush_depth += 1
        self.session.no_autoflush_enters += 1

    def __exit__(self, *_args: object) -> None:
        self.session.no_autoflush_depth -= 1
        self.session.no_autoflush_exits += 1


class _ReadSession:
    def __init__(
        self,
        *,
        pay_list: PayList | None,
        artifacts: list[PayListExportArtifact] | None = None,
        payments: list[GovPayment] | None = None,
        case_numbers: dict[str, str] | None = None,
    ) -> None:
        self.pay_list = pay_list
        self.artifacts = artifacts or []
        self.payments = payments or []
        self.case_numbers = case_numbers or {}
        self.no_autoflush_depth = 0
        self.no_autoflush_enters = 0
        self.no_autoflush_exits = 0
        self.statements: list[Select[tuple[object, ...]]] = []

    @property
    def no_autoflush(self) -> _NoAutoflush:
        return _NoAutoflush(self)

    def execute(self, statement: Select[tuple[object, ...]]) -> _Result:
        assert self.no_autoflush_depth == 1
        self.statements.append(statement)
        sql = str(statement)
        if "FROM t_pay_list_export_artifact" in sql:
            assert (
                "ORDER BY t_pay_list_export_artifact.generated_at ASC, "
                "t_pay_list_export_artifact.id ASC"
            ) in sql
            return _Result(self.artifacts)
        if "FROM t_gov_payment" in sql:
            assert "ORDER BY t_gov_payment.id ASC" in sql
            return _Result(self.payments)
        if "FROM t_case" in sql:
            return _Result(list(self.case_numbers.items()))
        if "FROM t_pay_list" in sql:
            return _Result([] if self.pay_list is None else [self.pay_list])
        raise AssertionError(f"unexpected select: {sql}")

    def add(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("PayList detail read called add")

    def add_all(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("PayList detail read called add_all")

    def flush(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("PayList detail read called flush")

    def commit(self) -> None:
        raise AssertionError("PayList detail read called commit")

    def rollback(self) -> None:
        raise AssertionError("PayList detail read called rollback")

    def refresh(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("PayList detail read called refresh")


class _ForbiddenClock:
    @classmethod
    def now(cls, *_args: object, **_kwargs: object) -> datetime:
        raise AssertionError("PayList detail read accessed the clock")


def _pay_list(**overrides: object) -> PayList:
    values: dict[str, object] = {
        "id": 7,
        "client_id": "client-1",
        "pay_list_no": "PL-000007",
        "status": "DRAFT",
        "currency": "CNY",
        "planned_pay_date": date(2026, 8, 15),
        "paid_date": None,
        "total_amount": Decimal("300.00"),
        "remark": "legacy",
        "list_type": "ANNUITY",
        "flow_dir": "OUTBOUND",
        "invoice_no_from": "INV-1",
        "invoice_no_to": "INV-2",
        "official_upload_template_status": None,
        "official_upload_template_name": None,
        "official_upload_batch_limit": None,
        "official_pay_list_boundary_note": None,
        "created_at": datetime(2026, 7, 20, 8, 0),
        "updated_at": datetime(2026, 7, 20, 9, 0),
        "created_by": "creator-1",
        "updated_by": "updater-1",
    }
    values.update(overrides)
    return PayList(**values)


def _payment(payment_id: int, case_id: str, amount: str) -> GovPayment:
    return GovPayment(
        id=payment_id,
        pay_list_id=7,
        case_id=case_id,
        fee_item_id=f"fee-{payment_id}",
        status="PLANNED",
        currency="CNY",
        paid_date=None,
        paid_amount=Decimal(amount),
        official_receipt_no=None,
        remark=f"payment-{payment_id}",
        fee_code="ANNUITY_GOV",
        year_no=2,
        planned_amt=Decimal(amount),
        planned_currency="CNY",
        paid_currency=None,
        voucher_no=None,
        invoice_no=None,
        created_at=datetime(2026, 7, 20, 10, payment_id),
        updated_at=datetime(2026, 7, 20, 11, payment_id),
        created_by="creator-1",
        updated_by=None,
    )


def _artifact(
    artifact_id: str,
    *,
    generated_at: datetime,
    kind: str,
    status: str,
) -> PayListExportArtifact:
    accepted = status == "OFFICIAL_SITE_ACCEPTED"
    return PayListExportArtifact(
        id=artifact_id,
        pay_list_id=7,
        kind=kind,
        status=status,
        content_sha256=artifact_id[0] * 64,
        managed_storage_path=f"pay-lists/7/{artifact_id}.xlsx",
        template_version="cnipa-v1" if kind == "OFFICIAL_XLSM" else None,
        generated_by="user-1",
        generated_at=generated_at,
        idempotency_key=f"export-{artifact_id}",
        official_acceptance_evidence_ref="receipt-1" if accepted else None,
        official_acceptance_evidence_hash="f" * 64 if accepted else None,
        official_accepted_at=datetime(2026, 7, 21, 12, 0) if accepted else None,
        updated_at=datetime(2026, 7, 21, 13, 0),
    )


def test_detail_preserves_exact_legacy_projection_without_backing_facts(monkeypatch) -> None:
    payments = [_payment(11, "case-1", "100.00"), _payment(12, "case-2", "200.00")]
    session = _ReadSession(
        pay_list=_pay_list(),
        payments=payments,
        case_numbers={"case-1": "CASE-001", "case-2": "CASE-002"},
    )
    monkeypatch.setattr(service, "datetime", _ForbiddenClock)

    result = service.get_pay_list_detail(session, pay_list_id=7)  # type: ignore[arg-type]

    assert tuple(result) == ("pay_list", "gov_payments")
    assert tuple(result["pay_list"]) == PAY_LIST_FIELDS
    assert [item["id"] for item in result["gov_payments"]] == [11, 12]
    assert all(tuple(item) == GOV_PAYMENT_FIELDS for item in result["gov_payments"])
    assert [item["case_no"] for item in result["gov_payments"]] == ["CASE-001", "CASE-002"]
    assert [item["paid_amount"] for item in result["gov_payments"]] == ["100.00", "200.00"]
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1


def test_detail_projects_all_artifacts_and_exact_official_workbook(monkeypatch) -> None:
    first = _artifact(
        "a-first",
        generated_at=datetime(2026, 7, 20, 8, 0),
        kind="INTERNAL_XLSX",
        status="GENERATED",
    )
    second = _artifact(
        "b-second",
        generated_at=datetime(2026, 7, 20, 8, 0),
        kind="OFFICIAL_XLSM",
        status="OFFICIAL_SITE_ACCEPTED",
    )
    session = _ReadSession(
        pay_list=_pay_list(
            official_upload_template_status="READY",
            official_upload_template_name="CNIPA-2026.xlsm",
            official_upload_batch_limit=500,
            official_pay_list_boundary_note="仅为上传载体",
        ),
        artifacts=[first, second],
    )
    monkeypatch.setattr(service, "datetime", _ForbiddenClock)

    result = service.get_pay_list_detail(session, pay_list_id=7)  # type: ignore[arg-type]

    assert tuple(result) == (
        "pay_list",
        "gov_payments",
        "export_artifacts",
        "official_workbook",
    )
    assert [item["id"] for item in result["export_artifacts"]] == ["a-first", "b-second"]
    assert all(tuple(item) == EXPORT_ARTIFACT_FIELDS for item in result["export_artifacts"])
    assert result["export_artifacts"][0]["kind"] == "INTERNAL_XLSX"
    assert result["export_artifacts"][0]["status"] == "GENERATED"
    assert result["export_artifacts"][1]["kind"] == "OFFICIAL_XLSM"
    assert result["export_artifacts"][1]["status"] == "OFFICIAL_SITE_ACCEPTED"
    assert result["export_artifacts"][1]["official_acceptance_evidence_ref"] == "receipt-1"
    assert result["export_artifacts"][1]["official_acceptance_evidence_hash"] == "f" * 64
    assert result["export_artifacts"][1]["official_accepted_at"] == datetime(2026, 7, 21, 12, 0)
    assert tuple(result["official_workbook"]) == OFFICIAL_WORKBOOK_FIELDS
    assert result["official_workbook"] == {
        "official_upload_template_status": "READY",
        "official_upload_template_name": "CNIPA-2026.xlsm",
        "official_upload_batch_limit": 500,
        "official_pay_list_boundary_note": "仅为上传载体",
    }
    assert result["gov_payments"] == []
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1


@pytest.mark.parametrize(
    ("artifacts", "pay_list", "expected_optional_key"),
    [
        (
            [
                _artifact(
                    "c-only",
                    generated_at=datetime(2026, 7, 20, 9, 0),
                    kind="INTERNAL_XLSX",
                    status="GENERATED",
                )
            ],
            _pay_list(),
            "export_artifacts",
        ),
        (
            [],
            _pay_list(official_upload_template_name="CNIPA-only.xlsm"),
            "official_workbook",
        ),
    ],
)
def test_detail_optional_projections_are_independent(
    artifacts: list[PayListExportArtifact],
    pay_list: PayList,
    expected_optional_key: str,
) -> None:
    result = service.get_pay_list_detail(  # type: ignore[arg-type]
        _ReadSession(pay_list=pay_list, artifacts=artifacts),
        pay_list_id=7,
    )

    assert set(result) == {"pay_list", "gov_payments", expected_optional_key}


def test_missing_pay_list_preserves_404_and_read_only_execution() -> None:
    session = _ReadSession(pay_list=None)

    with pytest.raises(BusinessError) as caught:
        service.get_pay_list_detail(session, pay_list_id=999)  # type: ignore[arg-type]

    assert caught.value.code == "PAY_LIST_NOT_FOUND"
    assert caught.value.status_code == 404
    assert session.no_autoflush_enters == 1
    assert session.no_autoflush_exits == 1
