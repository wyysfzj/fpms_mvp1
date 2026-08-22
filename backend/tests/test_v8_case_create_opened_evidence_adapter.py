from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    EvidenceReference,
    LifecycleEventCommand,
)
from app.modules.cases.lifecycle_service import apply_lifecycle_event
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
    T_BioDeposit,
    T_CaseInventor,
    T_Priority,
)


def _case_payload(*, case_no: str, client_id: str | None) -> dict[str, object]:
    return {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "fee_reduction": "0",
        "client_id": client_id,
        "title_cn": "案件新建证据适配测试",
    }


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/clients",
        headers=auth_headers,
        json={
            "client_code": f"V8-OPENED-{uuid4().hex[:8]}",
            "name_cn": "案件新建证据客户",
            "client_type": "CLIENT",
            "default_currency": "CNY",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.parametrize("with_client", (False, True))
def test_case_post_persists_exact_case_opened_snapshot_and_evidence(
    with_client: bool,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    client_id = _create_client(client, auth_headers) if with_client else None
    case_no = f"V8-OPENED-EVIDENCE-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(case_no=case_no, client_id=client_id),
    )

    assert response.status_code == 201, response.text
    case_id = response.json()["id"]
    snapshot = {
        "case_id": case_id,
        "case_no": case_no,
        "case_type": "NORMAL",
        "client_id": client_id,
    }
    snapshot_bytes = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    source_snapshot_hash = f"sha256:{hashlib.sha256(snapshot_bytes).hexdigest()}"
    expected_payload_json = json.dumps(
        {
            "evidence_schema": "FPMS_CASE_OPENED_EVIDENCE_V1",
            "source_snapshot": snapshot,
            "source_snapshot_hash": source_snapshot_hash,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        assert case is not None
        assert case.case_no == case_no
        assert case.case_type == "NORMAL"
        assert case.client_id == client_id
        assert case.status == "NOT_FILED"
        assert case.business_stage == "NEW_CASE"
        assert case.official_procedure_stage == "NOT_SUBMITTED"
        assert case.legal_status == "NOT_ESTABLISHED"
        assert case.lifecycle_verification_status == "CONFIRMED"
        assert case.lifecycle_revision == 1

        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        ).all()
        assert len(activities) == 1
        activity = activities[0]
        assert activity.sequence == 1
        assert activity.lane == "LIFECYCLE"
        assert activity.activity_type == "CASE_OPENED"
        assert activity.confirmation_status == "CONFIRMED"
        assert activity.idempotency_key == f"case-opened:{case_id}"
        assert activity.payload_json == expected_payload_json

        admin_user_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert activity.actor_id == admin_user_id

        evidence_rows = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert len(evidence_rows) == 1
        evidence = evidence_rows[0]
        assert evidence.case_id == case_id
        assert evidence.evidence_kind == "CASE_RECORD"
        assert evidence.object_type == "Case"
        assert evidence.object_id == case_id
        assert evidence.content_hash == source_snapshot_hash
        assert activity.effective_at == activity.occurred_at == evidence.captured_at
        assert activity.effective_at.tzinfo is None


def test_case_opened_replay_uses_immutable_activity_truth_after_case_mutation(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_no = f"V8-OPENED-REPLAY-{uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(case_no=case_no, client_id=None),
    )
    assert response.status_code == 201, response.text
    case_id = response.json()["id"]

    with session_factory() as transaction:
        case = transaction.get(Case, case_id)
        assert case is not None
        activity = transaction.scalar(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        )
        assert activity is not None
        evidence = transaction.scalar(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        )
        assert evidence is not None
        stored_payload = json.loads(activity.payload_json)
        command = LifecycleEventCommand(
            case_id=case_id,
            event_type="CASE_OPENED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=activity.effective_at,
            occurred_at=activity.occurred_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=evidence.case_id,
                    evidence_kind=evidence.evidence_kind,
                    object_type=evidence.object_type,
                    object_id=evidence.object_id,
                    content_hash=evidence.content_hash,
                    captured_at=evidence.captured_at,
                ),
            ),
            actor_id=activity.actor_id,
            idempotency_key=activity.idempotency_key,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=stored_payload,
        )

        case.case_no = f"V8-OPENED-MUTATED-{uuid4().hex[:8]}"
        case.case_type = "PCT_INTL"
        transaction.commit()

        replay = apply_lifecycle_event(command, transaction)

        assert replay.reused is True
        assert replay.activity_id == activity.id

        before = (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            ),
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == case_id)
            ),
            case.case_no,
            case.case_type,
            case.lifecycle_revision,
        )
        changed_payload = dict(stored_payload)
        changed_payload["source_snapshot_hash"] = f"sha256:{'f' * 64}"
        with pytest.raises(BusinessError) as exc_info:
            apply_lifecycle_event(replace(command, payload=changed_payload), transaction)

        assert exc_info.value.code == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
        assert exc_info.value.status_code == 409
        after = (
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEvent)
                .where(CaseActivityEvent.case_id == case_id)
            ),
            transaction.scalar(
                select(func.count())
                .select_from(CaseActivityEventEvidence)
                .where(CaseActivityEventEvidence.case_id == case_id)
            ),
            case.case_no,
            case.case_type,
            case.lifecycle_revision,
        )
        assert after == before


def test_case_post_commits_exactly_once(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_commit = Session.commit
    commit_calls = 0

    def tracked_commit(transaction: Session) -> None:
        nonlocal commit_calls
        commit_calls += 1
        original_commit(transaction)

    monkeypatch.setattr(Session, "commit", tracked_commit)

    response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json=_case_payload(
            case_no=f"V8-OPENED-COMMIT-{uuid4().hex[:8]}",
            client_id=None,
        ),
    )

    assert response.status_code == 201, response.text
    assert commit_calls == 1


def test_case_post_lifecycle_persistence_failure_rolls_back_all_writes_once(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    engine: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_no = f"V8-OPENED-ROLLBACK-{uuid4().hex[:8]}"
    original_flush = Session.flush
    flush_calls = 0

    def fail_after_lifecycle_flush(
        transaction: Session,
        *args: object,
        **kwargs: object,
    ) -> None:
        nonlocal flush_calls
        flush_calls += 1
        original_flush(transaction, *args, **kwargs)
        if flush_calls == 2:
            raise RuntimeError("injected lifecycle persistence failure")

    rollback_calls = 0

    def tracked_rollback(_connection: object) -> None:
        nonlocal rollback_calls
        rollback_calls += 1

    monkeypatch.setattr(Session, "flush", fail_after_lifecycle_flush)
    event.listen(engine, "rollback", tracked_rollback)
    try:
        response = client.post(
            "/api/v1/cases",
            headers=auth_headers,
            json={
                **_case_payload(case_no=case_no, client_id=None),
                "inventors": [{"seq": 1, "name_cn": "回滚发明人"}],
                "priorities": [
                    {
                        "seq": 1,
                        "country_code": "CN",
                        "prio_no": "ROLLBACK-PRIORITY",
                        "prio_date": "2026-07-15",
                    }
                ],
                "bio_deposits": [
                    {
                        "seq": 1,
                        "deposit_no": "ROLLBACK-BIO",
                        "deposit_unit_name": "CGMCC",
                        "deposit_date": "2026-07-15",
                        "name": "回滚菌种",
                    }
                ],
            },
        )
    finally:
        event.remove(engine, "rollback", tracked_rollback)

    assert response.status_code == 500, response.text
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert flush_calls == 2
    assert rollback_calls == 1
    with session_factory() as transaction:
        assert transaction.scalar(select(Case).where(Case.case_no == case_no)) is None
        assert transaction.scalars(select(T_CaseInventor)).all() == []
        assert transaction.scalars(select(T_Priority)).all() == []
        assert transaction.scalars(select(T_BioDeposit)).all() == []
        assert transaction.scalars(select(CaseActivityEvent)).all() == []
        assert transaction.scalars(select(CaseActivityEventEvidence)).all() == []
