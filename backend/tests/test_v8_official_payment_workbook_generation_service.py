from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.errors import BusinessError, raise_business_error
from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.annuity.official_payment_workbook_input_service import (
    ResolveWorkbookInputCommand,
    WorkbookInputResult,
)
from app.modules.annuity.verified_official_payment_workbook import OfficialPaymentRow

NOW = datetime(2026, 8, 13, 12, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000001"


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def scalar_one_or_none(self) -> object | None:
        return self.rows[0] if self.rows else None

    def scalars(self) -> _Result:
        return self

    def all(self) -> list[object]:
        return self.rows


class _Transaction:
    def __init__(self, *, artifact: PayListExportArtifact | None = None) -> None:
        self.pay_list = PayList(
            id=7,
            client_id="client-1",
            pay_list_no="PL-000007",
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("900.00"),
        )
        self.payments = [
            GovPayment(
                id=1,
                pay_list_id=7,
                case_id="case-1",
                status="PLANNED",
                currency="CNY",
                paid_amount=Decimal("900.00"),
                planned_amt=Decimal("900.00"),
                planned_currency="CNY",
            )
        ]
        self.artifact = artifact
        self.flushes = 0
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement: object) -> _Result:
        sql = str(statement)
        if "t_pay_list_export_artifact" in sql:
            return _Result([self.artifact] if self.artifact is not None else [])
        if "t_pay_list" in sql:
            return _Result([self.pay_list])
        if "t_gov_payment" in sql:
            return _Result(self.payments)
        raise AssertionError(f"unexpected statement: {sql}")

    def add(self, instance: object) -> None:
        if isinstance(instance, PayListExportArtifact):
            self.artifact = instance

    def flush(self) -> None:
        self.flushes += 1

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _row() -> OfficialPaymentRow:
    return OfficialPaymentRow(
        sequence_number=1,
        application_number="CN202610000001",
        business_type="专利",
        invoice_title="测试申请人有限公司",
        unified_social_credit_code="91110000TEST000001",
        fee_type="申请费",
        foreign_currency_amount=None,
        amount_cny=900,
        remark="TEST_ONLY",
    )


def _command(*, runtime_profile: str = "production") -> object:
    return service.GenerateOfficialPaymentWorkbookCommand(
        pay_list_id=7,
        rows=(_row(),),
        actor_id=ACTOR_ID,
        idempotency_key="official-workbook-1",
        generated_at=NOW,
        runtime_profile=runtime_profile,
    )


def _input(*, source_classification: str = "PRODUCTION") -> WorkbookInputResult:
    return WorkbookInputResult(
        version_id="input-version-1",
        scope_key="GLOBAL",
        source_classification=source_classification,
        template_version="2026.08",
        template_storage_path="/managed/current-template.xlsm",
        template_content_hash="a" * 64,
        upload_proof_storage_path="/managed/upload-proof.bin",
        upload_proof_content_hash="b" * 64,
        structure_snapshot_hash="c" * 64,
        workflow_status="APPROVED",
        activation_status="ACTIVE" if source_classification == "PRODUCTION" else "INACTIVE",
        effective_from=NOW,
        effective_to=None,
        supersedes_version_id=None,
        current_identity_key="GLOBAL" if source_classification == "PRODUCTION" else None,
        created_by=ACTOR_ID,
        validated_by=ACTOR_ID,
        validated_at=NOW,
        reviewed_by="00000000-0000-4000-8000-000000000002",
        reviewed_at=NOW,
        activated_by=ACTOR_ID if source_classification == "PRODUCTION" else None,
        activated_at=NOW if source_classification == "PRODUCTION" else None,
        retired_by=None,
        retired_at=None,
        retirement_reason=None,
        disposition="RESOLVED",
    )


def _install_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    resolved_input: WorkbookInputResult | None = None,
    activity_error: Exception | None = None,
    gate_available: bool = True,
) -> tuple[list[ResolveWorkbookInputCommand], list[object], list[object]]:
    resolutions: list[ResolveWorkbookInputCommand] = []
    adapter_rows: list[object] = []
    activities: list[object] = []
    activity_results: dict[str, tuple[object, object]] = {}
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(storage_dir=tmp_path))
    template_path = tmp_path / "controlled-input.xlsm"
    template_path.write_bytes(b"controlled-template-bytes")
    if resolved_input is not None:
        resolved_input = replace(
            resolved_input,
            template_storage_path=str(template_path),
            template_content_hash=sha256(template_path.read_bytes()).hexdigest(),
        )

    def resolve(_transaction: object, command: ResolveWorkbookInputCommand) -> WorkbookInputResult:
        resolutions.append(command)
        if resolved_input is None:
            raise_business_error(
                "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
                "Official payment workbook input configuration is required",
                status_code=409,
            )
        return resolved_input

    def fill(path: Path, rows: tuple[OfficialPaymentRow, ...]) -> bytes:
        assert path.name == "template.xlsm"
        assert path != template_path
        assert path.read_bytes() == template_path.read_bytes()
        adapter_rows.extend(rows)
        return b"verified-official-xlsm"

    def append(command: object, *_args: object, **_kwargs: object) -> object:
        activities.append(command)
        if activity_error is not None:
            raise activity_error
        existing = activity_results.get(command.idempotency_key)
        if existing is not None:
            previous_command, previous_result = existing
            if previous_command != command:
                raise BusinessError("LIFECYCLE_IDEMPOTENCY_CONFLICT", "conflict", status_code=409)
            return previous_result
        result = SimpleNamespace(activity_id=f"activity-{len(activity_results) + 1}")
        activity_results[command.idempotency_key] = (command, result)
        return result

    def resolve_gate(command: object, _transaction: object) -> object:
        if not gate_available or resolved_input is None:
            raise BusinessError("DECISION_GATE_NOT_CONFIRMED", "missing", status_code=409)
        return SimpleNamespace(
            resolved_scope_key="GLOBAL",
            source_reference=resolved_input.upload_proof_storage_path,
            source_version=resolved_input.template_version,
            decision_value=service._official_workbook_input_gate_snapshot(resolved_input),
        )

    monkeypatch.setattr(service, "resolve_workbook_input", resolve)
    monkeypatch.setattr(service, "fill_official_payment_workbook", fill)
    monkeypatch.setattr(service, "append_case_activity", append)
    monkeypatch.setattr(service, "resolve_decision_gate", resolve_gate)
    return resolutions, adapter_rows, activities


def test_generation_resolves_active_production_input_and_persists_distinct_fact(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    resolutions, adapter_rows, activities = _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(),
    )

    result = service.generate_official_payment_workbook(_command(), transaction)

    assert resolutions == [ResolveWorkbookInputCommand(at=NOW, runtime_profile="production")]
    assert adapter_rows == [_row()]
    assert result.content == b"verified-official-xlsm"
    assert result.content_sha256 == sha256(result.content).hexdigest()
    assert result.template_version == "2026.08"
    assert result.template_content_hash == sha256(b"controlled-template-bytes").hexdigest()
    assert result.workbook_input_version_id == "input-version-1"
    assert result.generated_status == "GENERATED"
    assert result.accepted is False
    assert result.paid is False
    assert result.ticket_verified is False
    assert result.managed_storage_path == f"official-payment-workbooks/7/{result.artifact_id}.xlsm"
    assert (tmp_path / result.managed_storage_path).read_bytes() == result.content

    artifact = transaction.artifact
    assert artifact is not None
    assert (artifact.kind, artifact.status, artifact.template_version) == (
        "OFFICIAL_XLSM",
        "GENERATED",
        "2026.08",
    )
    assert artifact.content_sha256 == result.content_sha256
    assert artifact.official_acceptance_evidence_ref is None
    assert artifact.official_acceptance_evidence_hash is None
    assert artifact.official_accepted_at is None
    assert transaction.pay_list.status == "DRAFT"
    assert transaction.payments[0].status == "PLANNED"
    assert transaction.commits == transaction.rollbacks == 0

    assert len(activities) == 1
    activity = activities[0]
    assert activity.case_id == "case-1"
    assert activity.lane.value == "FEE"
    assert activity.event_type == "OFFICIAL_PAYMENT_WORKBOOK_GENERATED"
    assert activity.payload["artifact_id"] == result.artifact_id
    assert activity.payload["workbook_input_version_id"] == "input-version-1"
    assert activity.payload["template_version"] == "2026.08"
    assert activity.payload["template_content_hash"] == result.template_content_hash
    assert len(activity.payload["rows_snapshot_hash"]) == 64
    assert activity.payload["generated_status"] == "GENERATED"
    assert activity.payload["accepted"] is False
    assert activity.payload["paid"] is False
    assert activity.payload["ticket_verified"] is False


@pytest.mark.parametrize(
    ("runtime_profile", "resolved_source"),
    [("production", None), ("production", "TEST_ONLY")],
)
def test_missing_or_test_only_production_input_fails_409_without_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    runtime_profile: str,
    resolved_source: str | None,
) -> None:
    transaction = _Transaction()
    _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(source_classification=resolved_source) if resolved_source else None,
    )

    with pytest.raises(BusinessError) as caught:
        service.generate_official_payment_workbook(
            _command(runtime_profile=runtime_profile),
            transaction,
        )

    assert caught.value.status_code == 409
    assert caught.value.code == "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED"
    assert transaction.artifact is None
    assert transaction.flushes == 0
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []
    assert transaction.commits == transaction.rollbacks == 0


def test_resolved_input_byte_drift_fails_before_adapter_or_product_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    _resolutions, adapter_rows, activities = _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(),
    )
    (tmp_path / "controlled-input.xlsm").write_bytes(b"changed-after-resolution-contract")

    with pytest.raises(BusinessError) as caught:
        service.generate_official_payment_workbook(_command(), transaction)

    assert caught.value.code == "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED"
    assert caught.value.status_code == 409
    assert adapter_rows == []
    assert activities == []
    assert transaction.artifact is None
    assert transaction.flushes == 0
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []


def test_missing_or_mismatched_production_gate_fails_without_write(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(),
        gate_available=False,
    )

    with pytest.raises(BusinessError) as caught:
        service.generate_official_payment_workbook(_command(), transaction)

    assert caught.value.code == "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED"
    assert caught.value.status_code == 409
    assert transaction.artifact is None
    assert transaction.flushes == 0
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []


def test_identical_replay_reuses_exact_artifact_activity_and_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    _resolutions, adapter_rows, activities = _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(),
    )

    first = service.generate_official_payment_workbook(_command(), transaction)
    second = service.generate_official_payment_workbook(_command(), transaction)

    assert second == first
    assert adapter_rows == [_row()]
    assert len(activities) == 2
    assert activities[1] == activities[0]
    assert transaction.flushes == 1


def test_differing_replay_and_multi_case_pay_list_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    _install_dependencies(monkeypatch, tmp_path, resolved_input=_input())
    service.generate_official_payment_workbook(_command(), transaction)
    differing_row = replace(_row(), amount_cny=901)
    with pytest.raises(BusinessError) as replay_error:
        service.generate_official_payment_workbook(
            replace(_command(), rows=(differing_row,)),
            transaction,
        )
    assert replay_error.value.code == "OFFICIAL_PAYMENT_WORKBOOK_IDEMPOTENCY_CONFLICT"

    second_transaction = _Transaction()
    second_transaction.payments.append(
        GovPayment(
            id=2,
            pay_list_id=7,
            case_id="case-2",
            status="PLANNED",
            currency="CNY",
            paid_amount=Decimal("900.00"),
            planned_amt=Decimal("900.00"),
            planned_currency="CNY",
        )
    )
    _install_dependencies(monkeypatch, tmp_path, resolved_input=_input())
    with pytest.raises(BusinessError) as multi_case_error:
        service.generate_official_payment_workbook(_command(), second_transaction)
    assert multi_case_error.value.code == "OFFICIAL_PAYMENT_WORKBOOK_NO_CASES"
    assert second_transaction.artifact is None


def test_adapter_or_activity_failure_leaves_no_durable_artifact_or_managed_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    adapter_failure = _Transaction()
    _install_dependencies(monkeypatch, tmp_path, resolved_input=_input())
    monkeypatch.setattr(
        service,
        "fill_official_payment_workbook",
        lambda *_args: (_ for _ in ()).throw(ValueError("adapter failed")),
    )
    with pytest.raises(ValueError, match="adapter failed"):
        service.generate_official_payment_workbook(_command(), adapter_failure)
    assert adapter_failure.artifact is None
    assert adapter_failure.flushes == 0
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []

    activity_failure = _Transaction()
    _install_dependencies(
        monkeypatch,
        tmp_path,
        resolved_input=_input(),
        activity_error=BusinessError("ACTIVITY_FAILED", "failed"),
    )
    with pytest.raises(BusinessError, match="ACTIVITY_FAILED"):
        service.generate_official_payment_workbook(_command(), activity_failure)
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []
    assert activity_failure.commits == activity_failure.rollbacks == 0


def test_concurrent_artifact_write_conflict_is_mapped_and_compensated(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    transaction = _Transaction()
    _install_dependencies(monkeypatch, tmp_path, resolved_input=_input())

    def fail_flush() -> None:
        raise IntegrityError("insert", {}, Exception("unique conflict"))

    monkeypatch.setattr(transaction, "flush", fail_flush)
    with pytest.raises(BusinessError) as caught:
        service.generate_official_payment_workbook(_command(), transaction)

    assert caught.value.code == "OFFICIAL_PAYMENT_WORKBOOK_IDEMPOTENCY_CONFLICT"
    assert caught.value.status_code == 409
    assert list(tmp_path.glob("official-payment-workbooks/**/*.xlsm")) == []
    assert transaction.commits == transaction.rollbacks == 0
