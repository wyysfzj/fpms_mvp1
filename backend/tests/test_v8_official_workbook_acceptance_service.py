from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from shutil import copyfile
from threading import Event, Lock
from types import SimpleNamespace

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.annuity import service
from app.modules.annuity.models import GovPayment, PayList, PayListExportArtifact
from app.modules.annuity.official_payment_workbook_input_service import (
    ActivateWorkbookInputCommand,
    RegisterWorkbookInputCommand,
    ReviewWorkbookInputCommand,
    ValidateWorkbookInputCommand,
    WorkbookInputResult,
    activate_workbook_input,
    register_workbook_input,
    review_workbook_input,
    validate_workbook_input,
)
from app.modules.annuity.verified_official_payment_workbook import OfficialPaymentRow
from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.masterdata.clients.models import Client
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateStatus,
    RecordDecisionGateCommand,
    record_decision_gate,
)
from app.modules.system.models import CustomerDecisionGate

NOW = datetime(2026, 8, 13, 13, 0)
CASE_ID = "00000000-0000-4000-8000-000000000100"
CLIENT_ID = "00000000-0000-4000-8000-000000000101"
USERS = tuple(f"00000000-0000-4000-8000-{index:012d}" for index in range(101, 105))
FIXTURE = Path(__file__).parent / "fixtures" / "v8_verified_official_payment_template.xlsm"


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
        remark="integration",
    )


def _command(
    artifact_id: str, **changes: object
) -> service.RecordOfficialWorkbookAcceptanceCommand:
    return replace(
        service.RecordOfficialWorkbookAcceptanceCommand(
            pay_list_id=7,
            artifact_id=artifact_id,
            evidence_ref="official-site/acceptance/receipt-1",
            evidence_sha256="a" * 64,
            accepted_at=NOW,
            actor_id=USERS[0],
            idempotency_key="acceptance-1",
            runtime_profile="production",
        ),
        **changes,
    )


def _create_input(
    db: Session,
    root: Path,
    *,
    source_classification: str,
    suffix: str,
) -> WorkbookInputResult:
    template = root / f"template-{suffix}.xlsm"
    proof = root / f"proof-{suffix}.json"
    copyfile(FIXTURE, template)
    proof.write_text(json.dumps({"source": source_classification}), encoding="utf-8")
    runtime_profile = "test" if source_classification == "TEST_ONLY" else "production"
    key = f"input-{suffix}"
    registered = register_workbook_input(
        db,
        RegisterWorkbookInputCommand(
            template_version=f"2026.08-{suffix}",
            template_storage_path=str(template),
            expected_template_hash=sha256(template.read_bytes()).hexdigest(),
            upload_proof_storage_path=str(proof),
            expected_upload_proof_hash=sha256(proof.read_bytes()).hexdigest(),
            effective_from=NOW - timedelta(days=1),
            effective_to=NOW + timedelta(days=1),
            source_classification=source_classification,
            actor_id=USERS[0],
            idempotency_key=key,
            runtime_profile=runtime_profile,
        ),
    )
    validate_workbook_input(
        db,
        ValidateWorkbookInputCommand(version_id=registered.version_id, actor_id=USERS[1]),
    )
    approved = review_workbook_input(
        db,
        ReviewWorkbookInputCommand(
            version_id=registered.version_id,
            decision="APPROVE",
            reason="集成测试独立复核受控输入",
            actor_id=USERS[2],
        ),
    )
    if source_classification == "TEST_ONLY":
        return approved
    return activate_workbook_input(
        db,
        ActivateWorkbookInputCommand(
            version_id=registered.version_id,
            actor_id=USERS[3],
            at=NOW - timedelta(hours=2),
            idempotency_key=key,
            runtime_profile="production",
        ),
    )


def _seed_business_rows(db: Session) -> None:
    db.add_all(
        T_User(
            id=user_id,
            username=f"acceptance-user-{index}",
            password_hash="test-only",
        )
        for index, user_id in enumerate(USERS, start=1)
    )
    db.add(Client(id=CLIENT_ID, name_cn="接受证据测试客户"))
    db.flush()
    db.add(
        Case(
            id=CASE_ID,
            case_no="CASE-ACCEPTANCE-1",
            client_id=CLIENT_ID,
            status="NOT_FILED",
        )
    )
    db.flush()
    db.add(
        PayList(
            id=7,
            client_id=CLIENT_ID,
            pay_list_no="PL-000007",
            status="DRAFT",
            currency="CNY",
            total_amount=Decimal("900.00"),
        )
    )
    db.flush()
    db.add(
        GovPayment(
            id=8,
            pay_list_id=7,
            case_id=CASE_ID,
            status="PLANNED",
            currency="CNY",
            paid_amount=Decimal("0"),
            planned_amt=Decimal("900.00"),
            planned_currency="CNY",
        )
    )
    db.flush()


def _seed_generated_artifact(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    source_classification: str,
) -> tuple[str, WorkbookInputResult]:
    storage = tmp_path / "storage"
    monkeypatch.setattr(service, "get_settings", lambda: SimpleNamespace(storage_dir=storage))
    with session_factory() as db:
        _seed_business_rows(db)
        resolved_input = _create_input(
            db,
            tmp_path,
            source_classification=source_classification,
            suffix="test" if source_classification == "TEST_ONLY" else "production",
        )
        if source_classification == "PRODUCTION":
            record_decision_gate(
                RecordDecisionGateCommand(
                    gate_code=DecisionGateCode.PAYMENT_WORKBOOK,
                    scope_key="GLOBAL",
                    decision_value=service._official_workbook_input_gate_snapshot(resolved_input),
                    decision_status=DecisionGateStatus.CONFIRMED,
                    source_reference=resolved_input.upload_proof_storage_path,
                    source_version=resolved_input.template_version,
                    confirmed_by=USERS[3],
                    effective_at=NOW - timedelta(hours=1),
                    idempotency_key="workbook-gate",
                    expected_current_gate_id=None,
                ),
                db,
            )
        generated = service.generate_official_payment_workbook(
            service.GenerateOfficialPaymentWorkbookCommand(
                pay_list_id=7,
                rows=(_row(),),
                actor_id=USERS[0],
                idempotency_key="generation-1",
                generated_at=NOW - timedelta(minutes=30),
                runtime_profile=("test" if source_classification == "TEST_ONLY" else "production"),
            ),
            db,
        )
        db.commit()
        return generated.artifact_id, resolved_input


def _activity_count(db: Session, activity_type: str) -> int:
    return (
        db.scalar(
            select(func.count(CaseActivityEvent.id)).where(
                CaseActivityEvent.activity_type == activity_type
            )
        )
        or 0
    )


def test_production_acceptance_binds_input_gate_generation_and_acceptance_lineage(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_id, input_version = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="PRODUCTION",
    )
    with session_factory() as db:
        result = service.record_official_workbook_acceptance(_command(artifact_id), db)
        db.commit()

    with session_factory() as db:
        artifact = db.get(PayListExportArtifact, artifact_id)
        pay_list = db.get(PayList, 7)
        payment = db.get(GovPayment, 8)
        acceptance = db.scalar(
            select(CaseActivityEvent).where(
                CaseActivityEvent.activity_type == "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED"
            )
        )
        evidence = db.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == acceptance.id
            )
        )
        generation = db.get(CaseActivityEvent, acceptance.source_activity_id)

        assert result.status == artifact.status == "OFFICIAL_SITE_ACCEPTED"
        assert result.activity_id == acceptance.id
        assert json.loads(generation.payload_json)["workbook_input_version_id"] == (
            input_version.version_id
        )
        assert json.loads(generation.payload_json)["template_content_hash"] == (
            input_version.template_content_hash
        )
        assert evidence.evidence_kind == "OFFICIAL_SITE_ACCEPTANCE_PROOF"
        assert evidence.object_id == artifact_id
        assert evidence.content_hash == "a" * 64
        assert (pay_list.status, payment.status, payment.official_receipt_no) == (
            "DRAFT",
            "PLANNED",
            None,
        )


def test_replay_conflict_and_caller_rollback_preserve_distinct_states(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_id, _input = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="PRODUCTION",
    )
    with session_factory() as db:
        service.record_official_workbook_acceptance(_command(artifact_id), db)
        db.rollback()
    with session_factory() as db:
        assert db.get(PayListExportArtifact, artifact_id).status == "GENERATED"
        assert _activity_count(db, "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED") == 0

    with session_factory() as db:
        first = service.record_official_workbook_acceptance(_command(artifact_id), db)
        db.commit()
    with session_factory() as db:
        replay = service.record_official_workbook_acceptance(_command(artifact_id), db)
        assert replace(replay, disposition="CREATED") == first
        assert replay.disposition == "REUSED"
        with pytest.raises(BusinessError) as caught:
            service.record_official_workbook_acceptance(
                _command(artifact_id, evidence_sha256="c" * 64),
                db,
            )
        assert (caught.value.code, caught.value.status_code) == (
            "OFFICIAL_WORKBOOK_ACCEPTANCE_CONFLICT",
            409,
        )
        assert _activity_count(db, "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED") == 1


@pytest.mark.parametrize("corruption", ["gate_source", "generation_input", "generation_hash"])
def test_production_gate_or_durable_generation_lineage_mismatch_is_409_no_write(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
) -> None:
    artifact_id, _input = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="PRODUCTION",
    )
    with session_factory() as db:
        if corruption == "gate_source":
            gate = db.scalar(select(CustomerDecisionGate))
            gate.source_reference = "/wrong/proof"
        else:
            generation = db.scalar(
                select(CaseActivityEvent).where(
                    CaseActivityEvent.activity_type == "OFFICIAL_PAYMENT_WORKBOOK_GENERATED"
                )
            )
            payload = json.loads(generation.payload_json)
            payload[
                "workbook_input_version_id"
                if corruption == "generation_input"
                else "template_content_hash"
            ] = "0" * 64
            generation.payload_json = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        db.commit()

    with session_factory() as db:
        with pytest.raises(BusinessError) as caught:
            service.record_official_workbook_acceptance(_command(artifact_id), db)
        assert caught.value.status_code == 409
        assert db.get(PayListExportArtifact, artifact_id).status == "GENERATED"
        assert _activity_count(db, "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED") == 0


def test_test_only_lineage_succeeds_without_production_gate(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    test_artifact_id, _test_input = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="TEST_ONLY",
    )
    with session_factory() as db:
        result = service.record_official_workbook_acceptance(
            _command(test_artifact_id, runtime_profile="test"),
            db,
        )
        assert result.disposition == "CREATED"
        db.rollback()


def test_profile_switch_of_production_artifact_to_test_only_input_fails(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_id, _production_input = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="PRODUCTION",
    )
    with session_factory() as db:
        _create_input(db, tmp_path, source_classification="TEST_ONLY", suffix="switch-test")
        db.commit()
    with session_factory() as db:
        with pytest.raises(BusinessError) as caught:
            service.record_official_workbook_acceptance(
                _command(artifact_id, runtime_profile="test"),
                db,
            )
        assert caught.value.status_code == 409
        assert db.get(PayListExportArtifact, artifact_id).status == "GENERATED"


def test_sqlite_immediate_writer_has_one_winner_and_one_lock_conflict(
    session_factory: sessionmaker[Session],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_id, _input = _seed_generated_artifact(
        session_factory,
        tmp_path,
        monkeypatch,
        source_classification="PRODUCTION",
    )
    original = service._ensure_sqlite_outer_transaction
    first_acquired = Event()
    release_first = Event()
    second_acquired = Event()
    acquisition_lock = Lock()
    acquisition_count = 0

    def synchronized_acquisition(transaction: Session) -> None:
        nonlocal acquisition_count
        with acquisition_lock:
            acquisition_count += 1
            ordinal = acquisition_count
        if ordinal == 1:
            original(transaction)
            first_acquired.set()
            assert release_first.wait(timeout=10)
            return
        transaction.connection().exec_driver_sql("PRAGMA busy_timeout = 0")
        acquired = False
        try:
            original(transaction)
            acquired = True
        finally:
            if acquired:
                second_acquired.set()
            release_first.set()

    monkeypatch.setattr(service, "_ensure_sqlite_outer_transaction", synchronized_acquisition)

    def attempt(index: int) -> str:
        with session_factory() as db:
            try:
                service.record_official_workbook_acceptance(
                    _command(
                        artifact_id,
                        evidence_ref=f"official-site/acceptance/receipt-{index}",
                        evidence_sha256=f"{index}" * 64,
                        idempotency_key=f"acceptance-{index}",
                    ),
                    db,
                )
                db.commit()
                return "CREATED"
            except BusinessError as exc:
                assert db.in_transaction()
                db.rollback()
                return f"{exc.code}:{exc.status_code}"

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(attempt, 1)
        assert first_acquired.wait(timeout=10)
        second = executor.submit(attempt, 2)
        outcomes = (first.result(timeout=10), second.result(timeout=10))
    assert outcomes == ("CREATED", "OFFICIAL_WORKBOOK_ACCEPTANCE_CONFLICT:409")
    assert not second_acquired.is_set()
    with session_factory() as db:
        artifact = db.get(PayListExportArtifact, artifact_id)
        assert artifact.status == "OFFICIAL_SITE_ACCEPTED"
        assert artifact.official_acceptance_evidence_ref.endswith("receipt-1")
        assert _activity_count(db, "OFFICIAL_PAYMENT_WORKBOOK_ACCEPTED") == 1
