from __future__ import annotations

import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from sqlalchemy.orm import Session

from app.core.errors import BusinessError
from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.cases.models import CaseActivityEvent, CaseActivityEventEvidence


class _Scalars:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def all(self) -> list[object]:
        return self.rows


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self.rows = rows

    def scalar_one_or_none(self) -> object | None:
        return self.rows[0] if self.rows else None

    def scalars(self) -> _Scalars:
        return _Scalars(self.rows)


class _Transaction:
    def __init__(
        self,
        *,
        pay_list: PayList,
        payments: list[GovPayment],
        artifact: PayListExportArtifact | None = None,
        activities: list[CaseActivityEvent] | None = None,
        evidence: list[CaseActivityEventEvidence] | None = None,
    ) -> None:
        self.pay_list = pay_list
        self.payments = payments
        self.artifact = artifact
        self.activities = activities or []
        self.evidence = evidence or []
        self.gov_payment_queries = 0
        self.flushes = 0
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    def execute(self, statement: object) -> _Result:
        sql = str(statement)
        if "t_pay_list_export_artifact" in sql:
            return _Result([self.artifact] if self.artifact is not None else [])
        if "t_case_activity_event_evidence" in sql:
            return _Result(self.evidence)
        if "t_case_activity_event" in sql:
            return _Result(self.activities)
        if "t_gov_payment" in sql:
            self.gov_payment_queries += 1
            return _Result(self.payments)
        if "t_client" in sql:
            return _Result([SimpleNamespace(name_cn="客户")])
        if "t_pay_list" in sql:
            return _Result([self.pay_list])
        raise AssertionError(f"unexpected statement: {sql}")

    def add(self, instance: object) -> None:
        if isinstance(instance, PayListExportArtifact):
            self.artifact = instance

    def flush(self) -> None:
        self.flushes += 1
        if self.artifact is not None and self.artifact.id is None:
            self.artifact.id = "artifact-1"

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        self.closes += 1


def _pay_list() -> PayList:
    return PayList(
        id=7,
        client_id="client-1",
        pay_list_no="PL-7",
        status="DRAFT",
        currency="CNY",
        total_amount=Decimal("300.00"),
    )


def _payment(case_id: str, payment_id: int) -> GovPayment:
    return GovPayment(
        id=payment_id,
        pay_list_id=7,
        case_id=case_id,
        status="PLANNED",
        currency="CNY",
        paid_amount=Decimal("100.00"),
        planned_amt=Decimal("100.00"),
        planned_currency="CNY",
    )


def _command(*, actor_id: str = "actor-1", key: str = "export-1") -> object:
    return service.ExportInternalPayListCommand(
        pay_list_id=7,
        actor_id=actor_id,
        idempotency_key=key,
    )


def _install_export_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
    *,
    activity_error: Exception | None = None,
) -> list[object]:
    commands: list[object] = []
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(storage_dir=tmp_path))
    monkeypatch.setattr(service, "build_pay_list_export_xlsx", lambda **_kwargs: b"xlsx-bytes")

    def append(command: object, *_args: object, **_kwargs: object) -> object:
        commands.append(command)
        if activity_error is not None:
            raise activity_error
        return SimpleNamespace(activity_id=f"activity-{len(commands)}")

    monkeypatch.setattr(service, "append_case_activity", append)
    return commands


def _activity_history(
    *,
    commands: list[object],
    activity_ids: tuple[str, ...],
) -> tuple[list[CaseActivityEvent], list[CaseActivityEventEvidence]]:
    activities: list[CaseActivityEvent] = []
    evidence: list[CaseActivityEventEvidence] = []
    for sequence, (command, activity_id) in enumerate(
        zip(commands, activity_ids, strict=True), start=1
    ):
        activities.append(
            CaseActivityEvent(
                id=activity_id,
                case_id=command.case_id,
                sequence=sequence,
                lane=command.lane.value,
                activity_type=command.event_type,
                source_activity_id=command.source_activity_id,
                occurred_at=command.occurred_at,
                effective_at=command.effective_at,
                confirmation_status=command.confirmation_status.value,
                old_business_stage=None,
                new_business_stage=None,
                old_official_procedure_stage=None,
                new_official_procedure_stage=None,
                old_legal_status=None,
                new_legal_status=None,
                actor_id=command.actor_id,
                reviewer_id=command.reviewer_id,
                idempotency_key=command.idempotency_key,
                supersedes_event_id=command.supersedes_event_id,
                payload_json=json.dumps(
                    command.payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        )
        reference = command.evidence_refs[0]
        evidence.append(
            CaseActivityEventEvidence(
                id=f"evidence-{sequence}",
                case_id=reference.case_id,
                activity_id=activity_id,
                evidence_kind=reference.evidence_kind,
                object_type=reference.object_type,
                object_id=reference.object_id,
                content_hash=reference.content_hash,
                captured_at=reference.captured_at,
            )
        )
    return activities, evidence


def _stored_activity_history(
    artifact: PayListExportArtifact,
    *case_ids: str,
) -> tuple[list[CaseActivityEvent], list[CaseActivityEventEvidence]]:
    commands = [
        SimpleNamespace(
            case_id=case_id,
            lane=SimpleNamespace(value="FEE"),
            event_type="PAY_LIST_INTERNAL_EXPORTED",
            source_activity_id=None,
            occurred_at=artifact.generated_at,
            effective_at=artifact.generated_at,
            confirmation_status=SimpleNamespace(value="CONFIRMED"),
            actor_id=artifact.generated_by,
            reviewer_id=None,
            idempotency_key=f"pay-list-internal-export:{artifact.id}:{case_id}",
            supersedes_event_id=None,
            payload={
                "artifact_id": artifact.id,
                "content_sha256": artifact.content_sha256,
                "managed_storage_path": artifact.managed_storage_path,
                "pay_list_id": artifact.pay_list_id,
            },
            evidence_refs=(
                SimpleNamespace(
                    case_id=case_id,
                    evidence_kind="PAY_LIST_EXPORT_ARTIFACT",
                    object_type="PayListExportArtifact",
                    object_id=artifact.id,
                    content_hash=artifact.content_sha256,
                    captured_at=artifact.generated_at,
                ),
            ),
        )
        for case_id in case_ids
    ]
    return _activity_history(
        commands=commands,
        activity_ids=tuple(f"activity-{index}" for index in range(1, len(commands) + 1)),
    )


def test_internal_pay_list_export_public_contract_is_exact() -> None:
    command_type = getattr(service, "ExportInternalPayListCommand", None)
    result_type = getattr(service, "ExportInternalPayListResult", None)
    export_service = getattr(service, "export_internal_pay_list", None)

    assert command_type is not None, "ExportInternalPayListCommand is absent"
    assert result_type is not None, "ExportInternalPayListResult is absent"
    assert export_service is not None, "export_internal_pay_list is absent"

    expected_command_fields = (
        ("pay_list_id", int),
        ("actor_id", str),
        ("idempotency_key", str),
    )
    expected_result_fields = (
        ("artifact_id", str),
        ("pay_list_id", int),
        ("filename", str),
        ("content_type", str),
        ("content", bytes),
        ("content_sha256", str),
        ("managed_storage_path", str),
        ("activity_ids", tuple[str, ...]),
        ("generated_at", datetime),
        ("idempotency_key", str),
        ("reused", bool),
    )
    for data_type, expected_fields in (
        (command_type, expected_command_fields),
        (result_type, expected_result_fields),
    ):
        assert is_dataclass(data_type)
        assert data_type.__dataclass_params__.frozen is True
        assert "__slots__" in data_type.__dict__
        type_hints = get_type_hints(data_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(data_type)) == (
            expected_fields
        )

    command_fields = fields(command_type)
    assert all(field.kw_only for field in command_fields)
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(command_type).parameters.values()
    )

    command = command_type(
        pay_list_id=1,
        actor_id="actor-1",
        idempotency_key="export-1",
    )
    assert not hasattr(command, "__dict__")
    with pytest.raises(FrozenInstanceError):
        command.pay_list_id = 2

    signature = inspect.signature(export_service)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(export_service) == {
        "command": command_type,
        "transaction": Session,
        "return": result_type,
    }


@pytest.mark.parametrize(
    ("case_ids", "expected_activity_ids"),
    [
        (["case-a"], ("activity-1",)),
        (["案-乙", "case-a", "案-乙"], ("activity-1", "activity-2")),
    ],
)
def test_fresh_export_persists_hashed_artifact_and_one_activity_per_sorted_case(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
    case_ids: list[str],
    expected_activity_ids: tuple[str, ...],
) -> None:
    pay_list = _pay_list()
    transaction = _Transaction(
        pay_list=pay_list,
        payments=[_payment(case_id, index) for index, case_id in enumerate(case_ids, start=1)],
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)

    result = service.export_internal_pay_list(_command(), transaction)

    assert result.content == b"xlsx-bytes"
    assert result.content_sha256 == sha256(result.content).hexdigest()
    assert result.managed_storage_path == f"pay-list-exports/7/{result.artifact_id}.xlsx"
    assert (tmp_path / result.managed_storage_path).read_bytes() == result.content
    assert result.activity_ids == expected_activity_ids
    assert result.reused is False
    assert transaction.artifact is not None
    assert (
        transaction.artifact.kind,
        transaction.artifact.status,
        transaction.artifact.generated_by,
        transaction.artifact.content_sha256,
    ) == ("INTERNAL_XLSX", "GENERATED", "actor-1", result.content_sha256)
    assert pay_list.status == "DRAFT"
    assert transaction.commits == transaction.rollbacks == transaction.closes == 0

    expected_cases = sorted(set(case_ids), key=lambda value: value.encode())
    assert [command.case_id for command in commands] == expected_cases
    for command in commands:
        assert command.event_type == "PAY_LIST_INTERNAL_EXPORTED"
        assert command.lane.value == "FEE"
        assert command.source_activity_id is None
        assert command.effective_at == command.occurred_at == result.generated_at
        assert command.idempotency_key == (
            f"pay-list-internal-export:{result.artifact_id}:{command.case_id}"
        )
        assert command.payload["artifact_id"] == result.artifact_id
        assert command.payload["pay_list_id"] == 7
        assert command.payload["content_sha256"] == result.content_sha256
        assert command.payload["managed_storage_path"] == result.managed_storage_path


def test_128_character_public_key_uses_bounded_artifact_activity_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    case_id = "c" * 36
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment(case_id, 1)],
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)

    result = service.export_internal_pay_list(_command(key="k" * 128), transaction)

    assert len(commands) == 1
    activity_key = commands[0].idempotency_key
    assert activity_key == f"pay-list-internal-export:{result.artifact_id}:{case_id}"
    assert len(activity_key) == 98
    assert len(activity_key) <= 128


@pytest.mark.parametrize("conflict", ["actor", "hash"])
def test_replay_does_not_rewrite_and_rejects_actor_or_hash_conflict(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
    conflict: str,
) -> None:
    stored = b"stored-xlsx"
    stored_hash = sha256(stored).hexdigest()
    artifact = PayListExportArtifact(
        id="artifact-replay",
        pay_list_id=7,
        kind="INTERNAL_XLSX",
        status="GENERATED",
        content_sha256=stored_hash,
        managed_storage_path="pay-list-exports/7/artifact-replay.xlsx",
        template_version=None,
        generated_by="actor-1",
        generated_at=datetime(2026, 7, 20, 8, 9, 10),
        idempotency_key="export-1",
    )
    path = tmp_path / artifact.managed_storage_path
    path.parent.mkdir(parents=True)
    path.write_bytes(stored if conflict != "hash" else b"corrupt")
    before = path.stat().st_mtime_ns
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-a", 1)],
        artifact=artifact,
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)

    if conflict == "actor":
        with pytest.raises(BusinessError) as caught:
            service.export_internal_pay_list(_command(actor_id="actor-2"), transaction)
        assert caught.value.status_code == 409
        assert caught.value.code == "PAY_LIST_EXPORT_IDEMPOTENCY_CONFLICT"
    elif conflict == "hash":
        with pytest.raises(BusinessError) as caught:
            service.export_internal_pay_list(_command(), transaction)
        assert caught.value.status_code == 409
        assert caught.value.code == "PAY_LIST_EXPORT_IDEMPOTENCY_CONFLICT"
    else:
        raise AssertionError(conflict)

    assert path.stat().st_mtime_ns == before
    assert commands == []
    assert transaction.flushes == 0
    assert transaction.commits == transaction.rollbacks == transaction.closes == 0


def test_exact_replay_returns_original_carrier_without_rewrite(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    content = b"stored-xlsx"
    artifact = PayListExportArtifact(
        id="artifact-replay",
        pay_list_id=7,
        kind="INTERNAL_XLSX",
        status="GENERATED",
        content_sha256=sha256(content).hexdigest(),
        managed_storage_path="pay-list-exports/7/artifact-replay.xlsx",
        template_version=None,
        generated_by="actor-1",
        generated_at=datetime(2026, 7, 20, 8, 9, 10),
        idempotency_key="export-1",
    )
    path = tmp_path / artifact.managed_storage_path
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    before = path.stat().st_mtime_ns
    activities, evidence = _stored_activity_history(artifact, "case-a")
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-a", 1)],
        artifact=artifact,
        activities=activities,
        evidence=evidence,
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)

    result = service.export_internal_pay_list(_command(), transaction)

    assert (
        result.artifact_id,
        result.content,
        result.content_sha256,
        result.managed_storage_path,
        result.generated_at,
        result.reused,
    ) == (
        artifact.id,
        content,
        artifact.content_sha256,
        artifact.managed_storage_path,
        artifact.generated_at,
        True,
    )
    assert path.stat().st_mtime_ns == before
    assert result.activity_ids == ("activity-1",)
    assert commands == []
    assert transaction.flushes == 0


@pytest.mark.parametrize("mutation", ["insert", "delete", "reassign"])
def test_replay_recovers_activity_ids_without_reading_mutated_payments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
    mutation: str,
) -> None:
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-b", 1), _payment("case-a", 2)],
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)
    command = _command(key=f"mutation-{mutation}")
    fresh = service.export_internal_pay_list(command, transaction)
    transaction.activities, transaction.evidence = _activity_history(
        commands=commands,
        activity_ids=fresh.activity_ids,
    )
    payment_queries_after_fresh = transaction.gov_payment_queries

    if mutation == "insert":
        transaction.payments.append(_payment("case-new", 3))
    elif mutation == "delete":
        transaction.payments.pop()
    elif mutation == "reassign":
        transaction.payments[0].case_id = "case-new"
    else:
        raise AssertionError(mutation)

    replay = service.export_internal_pay_list(command, transaction)

    assert replay.reused is True
    assert replay.activity_ids == fresh.activity_ids
    assert transaction.gov_payment_queries == payment_queries_after_fresh
    assert len(commands) == 2


def test_replay_fails_closed_on_append_only_activity_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-a", 1)],
    )
    commands = _install_export_dependencies(monkeypatch, tmp_path)
    command = _command(key="drift")
    fresh = service.export_internal_pay_list(command, transaction)
    transaction.activities, transaction.evidence = _activity_history(
        commands=commands,
        activity_ids=fresh.activity_ids,
    )
    transaction.activities[0].payload_json = '{"artifact_id":"drifted"}'

    with pytest.raises(BusinessError) as caught:
        service.export_internal_pay_list(command, transaction)

    assert caught.value.status_code == 409
    assert caught.value.code == "PAY_LIST_EXPORT_IDEMPOTENCY_CONFLICT"


def test_no_cases_and_post_write_failure_are_compensated_without_owning_transaction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    no_cases = _Transaction(pay_list=_pay_list(), payments=[])
    _install_export_dependencies(monkeypatch, tmp_path)
    with pytest.raises(BusinessError) as caught:
        service.export_internal_pay_list(_command(), no_cases)
    assert caught.value.status_code == 409
    assert caught.value.code == "PAY_LIST_EXPORT_NO_CASES"

    activity_failure = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-a", 1)],
    )
    _install_export_dependencies(
        monkeypatch,
        tmp_path,
        activity_error=BusinessError("ACTIVITY_FAILED", "failed"),
    )
    with pytest.raises(BusinessError, match="ACTIVITY_FAILED"):
        service.export_internal_pay_list(_command(key="activity-failure"), activity_failure)

    assert list(tmp_path.rglob("*.xlsx")) == []
    for transaction in (no_cases, activity_failure):
        assert transaction.commits == transaction.rollbacks == transaction.closes == 0


def test_storage_failure_is_compensated(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: object,
) -> None:
    blocked_storage = tmp_path / "not-a-directory"
    blocked_storage.write_bytes(b"occupied")
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(storage_dir=blocked_storage),
    )
    monkeypatch.setattr(service, "build_pay_list_export_xlsx", lambda **_kwargs: b"xlsx")
    transaction = _Transaction(
        pay_list=_pay_list(),
        payments=[_payment("case-a", 1)],
    )
    with pytest.raises(BusinessError) as caught:
        service.export_internal_pay_list(_command(), transaction)
    assert caught.value.code == "PAY_LIST_EXPORT_STORAGE_WRITE_FAILED"
    assert transaction.commits == transaction.rollbacks == transaction.closes == 0
