from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from app.core.errors import BusinessError
from app.modules.documents.models import Document
from app.modules.fees.models import FeeDraft, FeeItem, T_GrantFeeTask
from app.modules.grant_fees import service as grant_fee_service

ROOT = Path(__file__).resolve().parents[2]
SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests"
    / "demo-integrated-a.live-backend.spec.ts"
)


def _source() -> str:
    return SPEC.read_text(encoding="utf-8")


def _method(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def test_ia10_to_ia12_are_real_and_next_red_is_ia13() -> None:
    source = _source()
    for checkpoint in ("IA-10", "IA-11", "IA-12"):
        assert f"return this.red('{checkpoint}')" not in source
    assert "return this.red('IA-13')" in source
    assert "task7-checkpoints.json" in source


def test_original_grant_binds_visible_review_to_public_lifecycle() -> None:
    source = _source()
    method = _method(source, "async createGrantOriginal", "async replaceGrant")
    for token in (
        "GRANT_NOTICE_ORIGINAL",
        "OFFICIAL_NOTICE_009",
        "this.createDocumentViaVisibleUi",
        "await this.uploadRole",
        "this.publicLifecycleApi('GRANT_NOTICE'",
        "reviewed_evidence_version_id: binding.evidenceVersionId",
        "expected_content_hash: binding.contentHash",
        "recordGrantConsumer",
        "expected_deadline",
        "original_activity_id",
    ):
        assert token in method
    assert (
        "expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', "
        "'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED'])"
    ) in source


def test_replacement_grant_has_distinct_evidence_and_exact_lineage() -> None:
    source = _source()
    method = _method(source, "async replaceGrant", "async exerciseGrantGatesAndPay")
    for token in (
        "GRANT_NOTICE_REPLACEMENT",
        "supersedes_role",
        "GRANT_NOTICE_ORIGINAL",
        "this.publicLifecycleApi('GRANT_REPLACEMENT'",
        "await this.uploadRole",
        "this.publicLifecycleApi('GRANT_NOTICE'",
        "reviewed_evidence_version_id: binding.evidenceVersionId",
        "expected_content_hash: binding.contentHash",
        "recordGrantConsumer",
        "superseded_task_id",
        "replacement_predecessor_task_id",
        "replacement_activity_id",
        "original_activity_id",
        "supersedes_activity_id",
    ):
        assert token in method


def test_superseded_mutations_and_missing_fee_authority_are_observable_no_write() -> None:
    source = _source()
    method = _method(source, "async exerciseGrantGatesAndPay", "async createServiceDraft")
    for operation in (
        "GRANT_GENERATE_DRAFT",
        "GRANT_BATCH_INSTRUCTION",
        "GRANT_GENERATE_NOTICES",
        "GRANT_TASK_STATE",
    ):
        assert f"this.publicLifecycleApi('{operation}'" in method
    for token in (
        "blocked_observations",
        "before_snapshot",
        "after_snapshot",
        "expect(afterSnapshot).toEqual(beforeSnapshot)",
        "record_pay_instruction",
        "DEMO_OFFICIAL_FEE_CONFIG_REQUIRED",
        "missing_authority_status",
        "missing_authority_before",
        "missing_authority_after",
        "official_fee_carriers",
    ):
        assert token in method


def _create_ready_zero_grant_task(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
) -> tuple[str, str]:
    client_response = client.post(
        "/api/v1/clients",
        headers=auth_headers,
        json={
            "client_code": f"IA-GRANT-{uuid4().hex[:8]}",
            "name_cn": "虚构集成授权边界客户",
            "default_currency": "CNY",
        },
    )
    assert client_response.status_code == 201, client_response.text
    case_response = client.post(
        "/api/v1/cases",
        headers=auth_headers,
        json={
            "case_no": f"IA-GRANT-{uuid4().hex[:8]}",
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "fee_reduction": "0",
            "title_cn": "虚构集成授权边界案件",
            "client_id": client_response.json()["id"],
        },
    )
    assert case_response.status_code == 201, case_response.text
    case_id = case_response.json()["id"]
    with session_factory() as db:
        source = Document(
            case_id=case_id,
            doc_type="OFFICIAL",
            direction="IN",
            doc_date=date(2026, 8, 11),
            title="虚构授权通知来源",
        )
        db.add(source)
        db.flush()
        task = T_GrantFeeTask(
            case_id=case_id,
            source_document_id=source.id,
            due_date=date(2026, 11, 23),
            deadline_source="IMPORTED_OFFICIAL_NOTICE",
            deadline_confirmed_at=datetime(2026, 8, 11, 9, 0),
            gov_fee_amt=Decimal("0.00"),
            service_fee_amt=Decimal("0.00"),
            currency="CNY",
            client_instruction="PAY",
            notify_count=2,
            draft_generated=False,
            notice_sent=True,
            is_overdue=False,
        )
        db.add(task)
        db.commit()
        return case_id, task.id


def test_demo_missing_official_fee_authority_is_409_and_zero_write(
    client: TestClient,
    auth_headers: dict[str, str],
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    case_id, task_id = _create_ready_zero_grant_task(client, auth_headers, session_factory)

    response = client.post(
        f"/api/v1/grant-fee-tasks/{task_id}/generate-draft",
        headers=auth_headers,
    )

    assert response.status_code == 409, response.text
    assert response.json()["error"]["code"] == "DEMO_OFFICIAL_FEE_CONFIG_REQUIRED"
    with session_factory() as db:
        assert db.scalar(
            select(func.count()).select_from(FeeDraft).where(FeeDraft.case_id == case_id)
        ) == 0
        assert db.scalar(select(func.count()).select_from(FeeItem)) == 0
        task = db.get(T_GrantFeeTask, task_id)
        assert task is not None
        assert task.client_instruction == "PAY"
        assert task.draft_generated is False


def test_demo_lifecycle_can_hash_an_explicitly_unconfigured_fee_snapshot(
    monkeypatch,
) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    document = Document(
        id=str(uuid4()),
        case_id=str(uuid4()),
        direction="IN",
        doc_date=date(2026, 8, 11),
        title="虚构授权通知",
        extra_data='{"official_due_date":"2026-11-23"}',
    )

    snapshot = grant_fee_service._demo_unconfigured_grant_fee_snapshot(
        document=document,
        reviewed_evidence_version_id=str(uuid4()),
        expected_evidence_content_hash=f"sha256:{'a' * 64}",
    )

    assert snapshot is not None
    assert snapshot.lines == ()
    assert '"lines":[]' in snapshot.canonical_json
    assert len(snapshot.snapshot_hash) == 64


def test_demo_does_not_downgrade_present_but_invalid_fee_lines(monkeypatch) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    document = Document(
        id=str(uuid4()),
        case_id=str(uuid4()),
        direction="IN",
        doc_date=date(2026, 8, 11),
        title="虚构授权通知",
        extra_data='{"GrantFeeLines":[]}',
    )

    assert grant_fee_service._demo_unconfigured_grant_fee_snapshot(
        document=document,
        reviewed_evidence_version_id=str(uuid4()),
        expected_evidence_content_hash=f"sha256:{'b' * 64}",
    ) is None


def _unconfigured_stored_snapshot_payload() -> dict[str, object]:
    document = Document(
        id=str(uuid4()),
        case_id=str(uuid4()),
        direction="IN",
        doc_date=date(2026, 8, 11),
        title="虚构授权通知谱系",
        extra_data='{"official_due_date":"2026-11-23"}',
    )
    evidence_id = str(uuid4())
    content_hash = f"sha256:{'c' * 64}"
    snapshot = grant_fee_service._demo_unconfigured_grant_fee_snapshot(
        document=document,
        reviewed_evidence_version_id=evidence_id,
        expected_evidence_content_hash=content_hash,
    )
    assert snapshot is not None
    return {
        "grant_fee_lines_snapshot": snapshot.canonical_json,
        "grant_fee_lines_snapshot_hash": snapshot.snapshot_hash,
        "grant_fee_lines_schema": snapshot.schema,
        "source_document_id": document.id,
        "reviewed_evidence_version_id": evidence_id,
        "reviewed_evidence_content_hash": content_hash,
    }


def test_demo_replacement_can_revalidate_predecessor_unconfigured_snapshot(monkeypatch) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")

    grant_fee_service._validate_grant_notice_stored_snapshot(
        _unconfigured_stored_snapshot_payload()
    )


def test_non_demo_replacement_rejects_predecessor_unconfigured_snapshot(monkeypatch) -> None:
    monkeypatch.setenv("FPMS_ENV", "demo")
    monkeypatch.setenv("FPMS_DEMO_SCOPE", "LOCAL_ABC_E2E")
    payload = _unconfigured_stored_snapshot_payload()
    monkeypatch.setenv("FPMS_ENV", "dev")
    monkeypatch.delenv("FPMS_DEMO_SCOPE", raising=False)

    with pytest.raises(BusinessError) as caught:
        grant_fee_service._validate_grant_notice_stored_snapshot(payload)

    assert caught.value.code == "LIFECYCLE_IDEMPOTENCY_CONFLICT"
