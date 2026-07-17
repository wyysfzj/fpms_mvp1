from __future__ import annotations

import hashlib
import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.modules.auth.models import T_User
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
)

PATH = "/api/v1/cases/{case_id}/official-work-packages/filing-preparation/resolve"


def _create_case(session_factory: sessionmaker) -> str:
    with session_factory() as transaction:
        case = Case(
            id=str(uuid4()),
            case_no=f"V8-FILING-PREP-{uuid4().hex[:8].upper()}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            title_cn="递交准备开始证据适配测试案件",
            status="NOT_FILED",
            business_stage="NEW_CASE",
            official_procedure_stage="NOT_SUBMITTED",
            legal_status="NOT_ESTABLISHED",
            lifecycle_revision=0,
            lifecycle_verification_status="CONFIRMED",
        )
        transaction.add(case)
        transaction.commit()
        return case.id


def _resolve(client: TestClient, auth_headers: dict[str, str], *, case_id: str):
    return client.post(PATH.format(case_id=case_id), headers=auth_headers)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_resolve_api_records_exact_filing_preparation_activity_once(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory)

    created = _resolve(client, auth_headers, case_id=case_id)
    replayed = _resolve(client, auth_headers, case_id=case_id)

    assert created.status_code == 200, created.text
    assert replayed.status_code == 200, replayed.text
    package_id = created.json()["package"]["id"]
    assert replayed.json()["package"]["id"] == package_id

    with session_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert actor_id is not None
        package = transaction.get(OfficialWorkPackage, package_id)
        assert package is not None
        assert package.created_by == actor_id
        assert package.updated_by == actor_id

        snapshot = {
            "case_id": case_id,
            "id": package_id,
            "package_kind": "FILING_PREP",
            "resolve_key": f"FILING_PREP:{case_id}",
        }
        snapshot_hash = f"sha256:{hashlib.sha256(_canonical_json(snapshot).encode('utf-8')).hexdigest()}"
        expected_payload = {
            "evidence_schema": "FPMS_FILING_PREPARATION_EVIDENCE_V1",
            "source_snapshot": snapshot,
            "source_snapshot_hash": snapshot_hash,
        }

        activities = transaction.scalars(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        ).all()
        assert len(activities) == 1
        activity = activities[0]
        assert activity.activity_type == "FILING_PREPARATION_STARTED"
        assert activity.lane == "LIFECYCLE"
        assert activity.confirmation_status == "CONFIRMED"
        assert activity.actor_id == actor_id
        assert activity.idempotency_key == f"filing-preparation-started:{package_id}"
        assert activity.payload_json == _canonical_json(expected_payload)
        assert activity.effective_at == activity.occurred_at == package.created_at

        evidence_rows = transaction.scalars(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        ).all()
        assert len(evidence_rows) == 1
        evidence = evidence_rows[0]
        assert evidence.case_id == case_id
        assert evidence.evidence_kind == "FILING_WORK_PACKAGE"
        assert evidence.object_type == "OfficialWorkPackage"
        assert evidence.object_id == package_id
        assert evidence.content_hash == snapshot_hash
        assert evidence.captured_at == package.created_at


def test_existing_package_keeps_stable_creator_and_records_current_actor(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory)
    package_id = str(uuid4())
    historical_creator = "historical-package-creator"
    with session_factory() as transaction:
        transaction.add(
            OfficialWorkPackage(
                id=package_id,
                case_id=case_id,
                package_kind="FILING_PREP",
                status="PREPARING",
                resolve_key=f"FILING_PREP:{case_id}",
                created_by=historical_creator,
                updated_by=historical_creator,
            )
        )
        transaction.commit()

    response = _resolve(client, auth_headers, case_id=case_id)

    assert response.status_code == 200, response.text
    with session_factory() as transaction:
        package = transaction.get(OfficialWorkPackage, package_id)
        assert package is not None
        assert package.created_by == historical_creator
        activity = transaction.scalar(
            select(CaseActivityEvent).where(CaseActivityEvent.case_id == case_id)
        )
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        assert activity is not None
        assert activity.actor_id == actor_id


def test_existing_package_without_creator_fails_closed_without_activity(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory)
    package_id = str(uuid4())
    with session_factory() as transaction:
        transaction.add(
            OfficialWorkPackage(
                id=package_id,
                case_id=case_id,
                package_kind="FILING_PREP",
                status="PREPARING",
                resolve_key=f"FILING_PREP:{case_id}",
                created_by=None,
            )
        )
        transaction.commit()

    response = _resolve(client, auth_headers, case_id=case_id)

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "FILING_PREPARATION_PROVENANCE_CONFLICT"
    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        ) == 0


@pytest.mark.parametrize("tampered_part", ("payload", "evidence"))
def test_replay_rejects_changed_persisted_provenance(
    tampered_part: str,
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> None:
    case_id = _create_case(session_factory)
    created = _resolve(client, auth_headers, case_id=case_id)
    assert created.status_code == 200, created.text

    with session_factory() as transaction:
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
        if tampered_part == "payload":
            payload = json.loads(activity.payload_json)
            payload["source_snapshot_hash"] = f"sha256:{'f' * 64}"
            activity.payload_json = _canonical_json(payload)
        else:
            evidence.content_hash = f"sha256:{'e' * 64}"
        transaction.commit()

    replayed = _resolve(client, auth_headers, case_id=case_id)

    assert replayed.status_code == 409, replayed.text
    assert replayed.json()["error"]["code"] == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        ) == 1
        assert transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.case_id == case_id)
        ) == 1


@pytest.mark.parametrize("actor_id", ("", "   "))
def test_service_rejects_blank_actor(
    actor_id: str,
    session_factory: sessionmaker,
) -> None:
    from app.core.errors import BusinessError
    from app.modules.official_workflows.service import ensure_filing_preparation_package

    case_id = _create_case(session_factory)
    with session_factory() as transaction:
        with pytest.raises(BusinessError) as exc_info:
            ensure_filing_preparation_package(
                transaction,
                case_id=case_id,
                actor_id=actor_id,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.code == "FILING_PREPARATION_ACTOR_INVALID"


def test_service_leaves_all_writes_in_caller_transaction(
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.official_workflows.service import ensure_filing_preparation_package

    case_id = _create_case(session_factory)
    with session_factory() as transaction:
        monkeypatch.setattr(
            transaction,
            "commit",
            lambda: pytest.fail("service must not commit caller transaction"),
        )
        monkeypatch.setattr(
            transaction,
            "rollback",
            lambda: pytest.fail("service must not roll back caller transaction"),
        )

        ensure_filing_preparation_package(
            transaction,
            case_id=case_id,
            actor_id="caller-owned-actor",
        )

    with session_factory() as verification:
        assert verification.scalar(
            select(func.count())
            .select_from(OfficialWorkPackage)
            .where(OfficialWorkPackage.case_id == case_id)
        ) == 0
        assert verification.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        ) == 0
        assert verification.scalar(
            select(func.count())
            .select_from(OfficialWorkPackageManifest)
            .join(OfficialWorkPackage)
            .where(OfficialWorkPackage.case_id == case_id)
        ) == 0
        assert verification.scalar(
            select(func.count())
            .select_from(OfficialWorkPackageChecklist)
            .join(OfficialWorkPackage)
            .where(OfficialWorkPackage.case_id == case_id)
        ) == 0


def test_api_rolls_back_package_refresh_and_activity_on_lifecycle_failure(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.modules.official_workflows.service as service

    case_id = _create_case(session_factory)

    def fail_lifecycle(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("injected filing-preparation lifecycle failure")

    monkeypatch.setattr(service, "apply_lifecycle_event", fail_lifecycle)

    response = _resolve(client, auth_headers, case_id=case_id)

    assert response.status_code == 500, response.text
    with session_factory() as transaction:
        assert transaction.scalar(
            select(func.count())
            .select_from(OfficialWorkPackage)
            .where(OfficialWorkPackage.case_id == case_id)
        ) == 0
        assert transaction.scalar(
            select(func.count())
            .select_from(CaseActivityEvent)
            .where(CaseActivityEvent.case_id == case_id)
        ) == 0
