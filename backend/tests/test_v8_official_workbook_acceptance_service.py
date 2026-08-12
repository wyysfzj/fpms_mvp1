from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.errors import BusinessError
from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    ResolveDecisionGateCommand,
)

NOW = datetime(2026, 8, 13, 13, 0)
ACTOR_ID = "00000000-0000-4000-8000-000000000001"
ARTIFACT_ID = "00000000-0000-4000-8000-000000000010"
EVIDENCE_HASH = "a" * 64


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
    def __init__(self) -> None:
        self.pay_list = PayList(
            id=7,
            client_id="client-1",
            pay_list_no="PL-000007",
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("900.00"),
        )
        self.payment = GovPayment(
            id=1,
            pay_list_id=7,
            case_id="case-1",
            status="PLANNED",
            currency="CNY",
            paid_amount=Decimal("900.00"),
            planned_amt=Decimal("900.00"),
            planned_currency="CNY",
        )
        self.artifact = PayListExportArtifact(
            id=ARTIFACT_ID,
            pay_list_id=7,
            kind="OFFICIAL_XLSM",
            status="GENERATED",
            content_sha256="b" * 64,
            managed_storage_path=f"official-payment-workbooks/7/{ARTIFACT_ID}.xlsm",
            template_version="2026.08",
            generated_by=ACTOR_ID,
            generated_at=datetime(2026, 8, 13, 12, 0),
            idempotency_key="generation-1",
            official_acceptance_evidence_ref=None,
            official_acceptance_evidence_hash=None,
            official_accepted_at=None,
        )
        self.activity_id: str | None = None
        self.flushes = 0
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement: object) -> _Result:
        sql = str(statement)
        if "t_pay_list_export_artifact" in sql:
            return _Result([self.artifact])
        if "t_pay_list" in sql:
            return _Result([self.pay_list])
        if "t_gov_payment" in sql:
            return _Result([self.payment])
        if "t_case_activity_event" in sql:
            return _Result([self.activity_id] if self.activity_id else [])
        raise AssertionError(f"unexpected statement: {sql}")

    def flush(self) -> None:
        self.flushes += 1

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _command(**changes: object) -> object:
    command = service.RecordOfficialWorkbookAcceptanceCommand(
        pay_list_id=7,
        artifact_id=ARTIFACT_ID,
        evidence_ref="official-site/acceptance/receipt-1",
        evidence_sha256=EVIDENCE_HASH,
        accepted_at=NOW,
        actor_id=ACTOR_ID,
        idempotency_key="acceptance-1",
        runtime_profile="production",
    )
    return replace(command, **changes)


def _install_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    transaction: _Transaction,
    *,
    gate_available: bool = True,
) -> tuple[list[object], list[object]]:
    gates: list[object] = []
    activities: list[object] = []

    def resolve_gate(command: object, _transaction: object) -> object:
        gates.append(command)
        if not gate_available:
            raise BusinessError("DECISION_GATE_NOT_CONFIRMED", "missing", status_code=409)
        return SimpleNamespace(resolved_scope_key="GLOBAL", source_version="2026.08")

    def append(command: object, _transaction: object, **_kwargs: object) -> object:
        activities.append(command)
        reused = transaction.activity_id is not None
        transaction.activity_id = transaction.activity_id or "activity-1"
        if not reused:
            transaction.flush()
        return SimpleNamespace(activity_id=transaction.activity_id, reused=reused)

    monkeypatch.setattr(service, "resolve_decision_gate", resolve_gate)
    monkeypatch.setattr(service, "append_case_activity", append)
    return gates, activities


def test_records_and_replays_same_pay_list_acceptance_without_payment_or_ticket_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transaction = _Transaction()
    gates, activities = _install_dependencies(monkeypatch, transaction)

    first = service.record_official_workbook_acceptance(_command(), transaction)
    second = service.record_official_workbook_acceptance(_command(), transaction)

    assert first.disposition == "CREATED"
    assert replace(second, disposition="CREATED") == first
    assert second.disposition == "REUSED"
    assert first.status == "OFFICIAL_SITE_ACCEPTED"
    assert (first.accepted, first.paid, first.ticket_verified) == (True, False, False)
    assert transaction.artifact.status == "OFFICIAL_SITE_ACCEPTED"
    assert transaction.artifact.official_acceptance_evidence_ref == _command().evidence_ref
    assert transaction.artifact.official_acceptance_evidence_hash == EVIDENCE_HASH
    assert transaction.artifact.official_accepted_at == NOW
    assert transaction.pay_list.status == "DRAFT"
    assert transaction.payment.status == "PLANNED"
    assert transaction.commits == transaction.rollbacks == 0
    assert transaction.flushes == 1
    assert gates == [
        ResolveDecisionGateCommand(
            gate_code=DecisionGateCode.PAYMENT_WORKBOOK,
            scope_key="GLOBAL",
            as_of=NOW,
        ),
        ResolveDecisionGateCommand(
            gate_code=DecisionGateCode.PAYMENT_WORKBOOK,
            scope_key="GLOBAL",
            as_of=NOW,
        ),
    ]
    assert len(activities) == 2
    activity = activities[0]
    assert activities[1] == activity
    assert activity.case_id == "case-1"
    assert activity.lane.value == "FEE"
    assert activity.event_type == "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED"
    assert activity.idempotency_key == (
        f"official-workbook-acceptance:{ARTIFACT_ID}:acceptance-1:case-1"
    )
    assert activity.evidence_refs[0].evidence_kind == "OFFICIAL_SITE_ACCEPTANCE_PROOF"
    assert activity.evidence_refs[0].object_id == ARTIFACT_ID
    assert activity.evidence_refs[0].content_hash == EVIDENCE_HASH
    assert activity.payload == {
        "accepted": True,
        "accepted_at": NOW.isoformat(timespec="microseconds"),
        "artifact_id": ARTIFACT_ID,
        "evidence_ref": "official-site/acceptance/receipt-1",
        "evidence_sha256": EVIDENCE_HASH,
        "generated_status": "GENERATED",
        "paid": False,
        "pay_list_id": 7,
        "ticket_verified": False,
    }


def test_missing_gate_or_conflicting_replay_fails_409_without_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing_gate = _Transaction()
    _install_dependencies(monkeypatch, missing_gate, gate_available=False)
    with pytest.raises(BusinessError) as caught:
        service.record_official_workbook_acceptance(_command(), missing_gate)
    assert (caught.value.code, caught.value.status_code) == (
        "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
        409,
    )
    assert missing_gate.artifact.status == "GENERATED"
    assert missing_gate.flushes == 0

    conflict = _Transaction()
    _install_dependencies(monkeypatch, conflict)
    service.record_official_workbook_acceptance(_command(), conflict)
    with pytest.raises(BusinessError) as replay_error:
        service.record_official_workbook_acceptance(
            _command(evidence_sha256="c" * 64),
            conflict,
        )
    assert (replay_error.value.code, replay_error.value.status_code) == (
        "OFFICIAL_WORKBOOK_ACCEPTANCE_CONFLICT",
        409,
    )
    assert conflict.artifact.official_acceptance_evidence_hash == EVIDENCE_HASH
    assert conflict.pay_list.status == "DRAFT"
    assert conflict.payment.status == "PLANNED"


def test_test_profile_isolated_path_skips_production_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    transaction = _Transaction()
    gates, _activities = _install_dependencies(monkeypatch, transaction)

    result = service.record_official_workbook_acceptance(
        _command(runtime_profile="test"),
        transaction,
    )

    assert result.disposition == "CREATED"
    assert gates == []
